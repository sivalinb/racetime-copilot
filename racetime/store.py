"""Durable accounts, leased jobs, evidence and provider usage. Never store keys."""
import hashlib, hmac, json, re, secrets, sqlite3, time, uuid
from contextlib import contextmanager
from pathlib import Path
from .config import DATA, MAX_CALLS, DAILY_CALLS

class Store:
    def __init__(self, path=None):
        self.path = Path(path or DATA / 'product.sqlite')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as c:
            c.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,name TEXT UNIQUE,salt TEXT,password TEXT,failures INTEGER DEFAULT 0,locked_until REAL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,owner TEXT,kind TEXT,status TEXT,payload TEXT,result TEXT,error TEXT,created REAL,updated REAL,lease REAL DEFAULT 0,attempts INTEGER DEFAULT 0,cancel INTEGER DEFAULT 0);
            CREATE INDEX IF NOT EXISTS jobs_owner ON jobs(owner,created);
            CREATE TABLE IF NOT EXISTS usage(id TEXT PRIMARY KEY,owner TEXT,job TEXT,purpose TEXT,created REAL,input_tokens INTEGER DEFAULT 0,output_tokens INTEGER DEFAULT 0,status TEXT DEFAULT 'reserved');
            CREATE TABLE IF NOT EXISTS media(id TEXT PRIMARY KEY,owner TEXT,payload TEXT);
            CREATE TABLE IF NOT EXISTS evidence(id TEXT,media TEXT,payload TEXT,vector TEXT,PRIMARY KEY(id,media));
            CREATE TABLE IF NOT EXISTS windows(media TEXT,start REAL,end REAL,PRIMARY KEY(media,start,end));
            CREATE TABLE IF NOT EXISTS window_notes(media TEXT,start REAL,end REAL,notes TEXT,PRIMARY KEY(media,start,end));
            ''')
    @contextmanager
    def db(self):
        c=sqlite3.connect(self.path,timeout=30);c.row_factory=sqlite3.Row
        try:
            yield c;c.commit()
        except BaseException:
            c.rollback();raise
        finally:c.close()
    def register(self,name,password):
        name=name.strip().lower()
        if not re.fullmatch(r'[a-z0-9_.-]{3,40}',name):raise ValueError('Use 3–40 letters, numbers, dots or underscores for the username.')
        if not 12 <= len(password) <= 256:raise ValueError('Use a password with 12–256 characters.')
        salt=secrets.token_hex(16);digest=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),600000).hex()
        try:
            with self.db() as c:c.execute('INSERT INTO users(id,name,salt,password) VALUES(?,?,?,?)',(str(uuid.uuid4()),name,salt,digest))
        except sqlite3.IntegrityError:raise ValueError('That username is unavailable.') from None
    def login(self,name,password):
        with self.db() as c:
            row=c.execute('SELECT * FROM users WHERE name=?',(name.strip().lower(),)).fetchone()
            salt=bytes.fromhex(row['salt']) if row else bytes(16)
            digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,600000).hex()
            valid=bool(row and hmac.compare_digest(digest,row['password']) and row['locked_until']<time.time())
            if row and not valid:c.execute('UPDATE users SET failures=failures+1,locked_until=CASE WHEN failures>=4 THEN ? ELSE locked_until END WHERE id=?',(time.time()+300,row['id']))
            if valid:c.execute('UPDATE users SET failures=0,locked_until=0 WHERE id=?',(row['id'],))
        if not valid:raise ValueError('Unable to sign in. Check your details; repeated failures pause login for five minutes.')
        return row['id']
    def media(self,owner,id):
        with self.db() as c:r=c.execute('SELECT payload FROM media WHERE id=? AND owner=?',(id,owner)).fetchone()
        if not r:raise ValueError('Video not found in your account.')
        return json.loads(r[0])
    def save_media(self,owner,m):
        with self.db() as c:
            old=c.execute('SELECT owner FROM media WHERE id=?',(m['id'],)).fetchone()
            if old and old[0]!=owner:raise ValueError('Video belongs to another account.')
            c.execute('INSERT INTO media VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',(m['id'],owner,json.dumps(m)))
    def all_media(self,owner):
        with self.db() as c:return [json.loads(r[0]) for r in c.execute('SELECT payload FROM media WHERE owner=?',(owner,))]
    def save_window(self,owner,media,start,end,events,vectors,limitations=None):
        self.media(owner,media)
        with self.db() as c:
            for row in c.execute('SELECT id,payload FROM evidence WHERE media=?',(media,)).fetchall():
                old=json.loads(row['payload'])
                if start<=old['start']<old['end']<=end:c.execute('DELETE FROM evidence WHERE id=? AND media=?',(row['id'],media))
            for e,v in zip(events,vectors,strict=True):c.execute('INSERT OR REPLACE INTO evidence VALUES(?,?,?,?)',(e['id'],media,json.dumps(e),json.dumps(v)))
            c.execute('INSERT OR IGNORE INTO windows VALUES(?,?,?)',(media,start,end))
            c.execute('INSERT OR REPLACE INTO window_notes VALUES(?,?,?,?)',(media,start,end,json.dumps(limitations or [])))
    def observations(self,owner,media):
        self.media(owner,media)
        with self.db() as c:return [(json.loads(r[0]),json.loads(r[1])) for r in c.execute('SELECT payload,vector FROM evidence WHERE media=?',(media,))]
    def windows(self,owner,media):
        self.media(owner,media)
        with self.db() as c:return [list(r) for r in c.execute('SELECT start,end FROM windows WHERE media=? ORDER BY start',(media,))]
    def coverage(self,owner,media,start,end):
        windows=self.windows(owner,media);cursor=start;gaps=[]
        for a,b in windows:
            if b<=cursor or a>=end:continue
            if a>cursor:gaps.append([cursor,min(a,end)])
            cursor=max(cursor,min(b,end))
        if cursor<end:gaps.append([cursor,end])
        with self.db() as c:
            notes=[note for r in c.execute('SELECT notes FROM window_notes WHERE media=? AND start<? AND end>?',(media,end,start)) for note in json.loads(r[0])]
        return {'coverage':windows,'gaps':gaps,'limitations':list(dict.fromkeys(notes))}
    def enqueue(self,owner,kind,payload):
        if kind not in {'analyze','recap','live'}:raise ValueError('Unknown job type.')
        id=str(uuid.uuid4());now=time.time()
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute("SELECT COUNT(*) FROM jobs WHERE owner=? AND status IN ('queued','running')",(owner,)).fetchone()[0]>=3:raise ValueError('Finish or cancel existing jobs first (three active jobs per account).')
            c.execute('INSERT INTO jobs(id,owner,kind,status,payload,created,updated) VALUES(?,?,?,?,?,?,?)',(id,owner,kind,'queued',json.dumps(payload),now,now))
        return id
    def job(self,owner,id):
        with self.db() as c:r=c.execute('SELECT * FROM jobs WHERE id=? AND owner=?',(id,owner)).fetchone()
        if not r:raise ValueError('Job not found in your account.')
        r=dict(r)
        for k in ['payload','result']:r[k]=json.loads(r[k]) if r[k] else None
        return r
    def jobs(self,owner):
        with self.db() as c:ids=[r[0] for r in c.execute('SELECT id FROM jobs WHERE owner=? ORDER BY created DESC LIMIT 50',(owner,))]
        return [self.job(owner,i) for i in ids]
    def claim(self):
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE');now=time.time()
            c.execute("UPDATE jobs SET status='queued',lease=0 WHERE status='running' AND lease<? AND attempts<3 AND cancel=0 AND kind!='live'",(now,))
            c.execute("UPDATE jobs SET status='failed',error='Live capture was interrupted. Recorded windows remain available; start a new capture with the current elapsed time.' WHERE kind='live' AND status='running' AND lease<?",(now,))
            c.execute("UPDATE jobs SET status='failed',error='Worker stopped repeatedly; create a new job.' WHERE status='running' AND lease<? AND attempts>=3",(now,))
            c.execute("UPDATE jobs SET status='cancelled' WHERE cancel=1 AND status IN ('running','queued') AND lease<?",(now,))
            r=c.execute("SELECT id,owner FROM jobs WHERE status='queued' AND cancel=0 ORDER BY created LIMIT 1").fetchone()
            if not r:return None
            c.execute("UPDATE jobs SET status='running',lease=?,updated=?,attempts=attempts+1 WHERE id=?",(now+180,now,r['id']))
        return self.job(r['owner'],r['id'])
    def heartbeat(self,id):
        with self.db() as c:c.execute("UPDATE jobs SET lease=? WHERE id=? AND status='running'",(time.time()+180,id))
    def finish(self,owner,id,status,result=None,error=None):
        if status not in {'completed','awaiting_review','failed','cancelled','running'}:raise ValueError('Invalid job status.')
        with self.db() as c:c.execute('UPDATE jobs SET status=?,result=?,error=?,updated=?,lease=0 WHERE id=? AND owner=?',(status,json.dumps(result) if result is not None else None,error,time.time(),id,owner))
    def cancel(self,owner,id):
        self.job(owner,id)
        with self.db() as c:c.execute('UPDATE jobs SET cancel=1 WHERE id=? AND owner=?',(id,owner))
    def reserve(self,owner,job,purpose):
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT COUNT(*) FROM usage WHERE job=?',(job,)).fetchone()[0]>=MAX_CALLS:raise ValueError('This job reached its provider-call budget. Use a shorter interval.')
            if c.execute('SELECT COUNT(*) FROM usage WHERE owner=? AND created>?',(owner,time.time()-86400)).fetchone()[0]>=DAILY_CALLS:raise ValueError('Daily provider-call budget reached.')
            id=str(uuid.uuid4());c.execute('INSERT INTO usage(id,owner,job,purpose,created) VALUES(?,?,?,?,?)',(id,owner,job,purpose,time.time()))
        return id
    def used(self,id,input_tokens=0,output_tokens=0,status='ok'):
        with self.db() as c:c.execute('UPDATE usage SET input_tokens=?,output_tokens=?,status=? WHERE id=?',(input_tokens,output_tokens,status,id))
    def usage(self,owner):
        with self.db() as c:return dict(c.execute('SELECT COUNT(*) calls,COALESCE(SUM(input_tokens),0) input_tokens,COALESCE(SUM(output_tokens),0) output_tokens FROM usage WHERE owner=? AND created>?',(owner,time.time()-86400)).fetchone())
