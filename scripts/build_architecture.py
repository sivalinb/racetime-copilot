"""Generate dependency-free, editable SVG architecture plates from the implemented design."""
from pathlib import Path
from html import escape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public'/'architecture'
OUT.mkdir(parents=True,exist_ok=True)
BG='#eef2f5'; INK='#1b293a'; MUTED='#506176'; LINE='#becbd5'
BLUE='#286487'; BLUE_BG='#dfeef5'; AMBER='#9a6922'; AMBER_BG='#fbefd7'
GREEN='#287462'; GREEN_BG='#deefe8'; RED='#a04b3e'; RED_BG='#f7e5df'; WHITE='#ffffff'
class Plate:
    def __init__(self,title,subtitle,h,description):
        self.h=h
        self.items=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" role="img" aria-labelledby="title description">',f'<title id="title">{escape(title)}</title><desc id="description">{escape(description)}</desc>',f'<rect width="1600" height="{h}" fill="{BG}"/>','<defs>']
        for name,color in [('arrow',INK),('blue',BLUE),('green',GREEN),('red',RED)]:
            self.items.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker>')
        self.items.append('</defs>')
        self.text(40,35,'RACETIME COPILOT / ENGINEERING PLATES',15,MUTED,True,True)
        self.text(40,75,title,32,INK,True)
        self.text(40,108,subtitle,17,MUTED)
        self.line([(40,125),(1560,125)],LINE,arrow=False)
        for x,color,label in [(40,BLUE,'APPLICATION / RULES'),(400,AMBER,'MODEL OPERATION'),(755,GREEN,'HUMAN REVIEW / RESULT'),(1170,RED,'BLOCKED / UNVERIFIED')]:
            self.rect(x,139,13,13,color,color,3);self.text(x+22,151,label,13,MUTED,True,True)
    def text(self,x,y,text,size=17,color=INK,bold=False,mono=False,anchor='start'):
        family='Courier New, monospace' if mono else 'Arial, Helvetica, sans-serif'
        self.items.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{escape(text)}</text>')
    def rect(self,x,y,w,h,fill=WHITE,stroke=LINE,r=10,dash=False):
        d=' stroke-dasharray="7 5"' if dash else ''
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{d}/>')
    def line(self,points,color=INK,arrow=True,dash=False,marker='arrow'):
        a=f' marker-end="url(#{marker})"' if arrow else '';d=' stroke-dasharray="7 5"' if dash else ''
        self.items.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="1.8"{a}{d}/>')
    def card(self,x,y,w,h,title,lines,kind='plain',code=None,size=17,title_size=21):
        color,fill={'plain':(LINE,WHITE),'app':(BLUE,BLUE_BG),'model':(AMBER,AMBER_BG),'human':(GREEN,GREEN_BG),'blocked':(RED,RED_BG)}[kind]
        self.rect(x,y,w,h,fill,color)
        self.rect(x,y+12,4,h-24,color,color,0)
        self.text(x+18,y+30,title,title_size,INK,True)
        yy=y+56
        if code:
            self.text(x+18,yy,code,14,MUTED,False,True);yy+=25
        for line in lines:self.text(x+18,yy,line,size,MUTED);yy+=24
        assert yy-24 <= y+h-10,(title,yy,y+h)
    def tag(self,x,y,text,color=MUTED):self.text(x,y,text,14,color,True,True)
    def footer(self,y,line1,line2):
        self.line([(40,y),(1560,y)],LINE,arrow=False)
        self.text(40,y+27,line1,15,MUTED)
        self.text(40,y+52,line2,14,MUTED)
    def save(self,name):
        (OUT/name).write_text('\n'.join(self.items+['</svg>']))

p=Plate('I. System architecture','The local video product, its model boundary, persistent state and separate capstone components.',1640,'RaceTime system component diagram. Streamlit submits account-scoped jobs to a SQLite-backed worker. LangGraph coordinates video inspection, semantic retrieval, cited synthesis and durable review. Gemini, storage, evaluation and optional deployment are identified, with validation limits.')
p.tag(40,180,'INPUTS');p.tag(545,180,'LOCAL APPLICATION');p.tag(1120,180,'SERVICES + PERSISTENCE')
p.card(40,200,455,135,'Video sources + question',['Public YouTube URL or local video','start / end / as_of + question','MP4 / MOV / WebM; upload <= 100 MB'])
p.card(545,200,510,135,'Streamlit UI :8501',['Save media; queue work; inspect results','Review / export; human evaluation'],kind='app',code='app.py + racetime/ui.py')
p.card(1120,200,440,135,'Account + media records',['SQLite: users, media','Salted PBKDF2; owner-scoped reads','Uploads <= 500 MB / account'])
p.line([(495,267),(545,267)]);p.line([(1055,267),(1120,267)])
p.card(40,390,455,135,'Live capture worker',['yt-dlp -> FFmpeg -> 60 s segments','<= 15 min; elapsed origin supplied','Clock alignment / active test pending'],kind='blocked')
p.card(545,390,510,135,'Durable background jobs',['claim -> process -> heartbeat -> finish','3 active / account; recorded-job recovery'],kind='app',code='worker.py + Service.process_one()')
p.card(1120,390,440,135,'Job queue + call meter',['SQLite: jobs, usage; WAL transactions','180 s lease; 20 s heartbeat','32 calls / job; 120 / account / 24 h'])
p.line([(800,335),(800,390)]);p.tag(820,367,'enqueue')
p.line([(545,457),(495,457)]);p.text(517,442,'live',12,MUTED,mono=True,anchor='middle')
p.line([(1055,457),(1120,457)])
p.rect(40,590,1015,295,WHITE,BLUE,dash=True)
p.tag(60,618,'LANGGRAPH / racetime/agent.py',BLUE)
p.rect(60,637,975,54,BLUE_BG,BLUE)
p.text(78,659,'State: question + media + start/end/as_of + selected + iterations',16,INK,mono=True)
p.text(78,681,'       inspected/retrieved + narrative + review + coverage/gaps + trace',15,MUTED,mono=True)
p.card(60,715,295,142,'1 / Legal actions',['Cold source: inspect after retrieval','Then: inspect / summarize / clarify','Iteration cap; one legal action','uses a rule, without an LLM call'],kind='app',size=14,title_size=19)
p.card(400,715,295,142,'2 / Model choice',['Gemini returns action + reason','Pydantic / JSON Schema contract','Action must be in permitted set','Only called when there is a choice'],kind='model',size=14,title_size=19)
p.card(740,715,295,142,'3 / Rule fallback',['Illegal action or planner failure','falls back to a permitted action','Trace mode: rule / llm / fallback','No invented successful inspection'],kind='app',size=14,title_size=19)
p.line([(355,787),(400,787)]);p.line([(695,787),(740,787)],dash=True)
p.line([(800,525),(800,590)]);p.tag(820,563,'recap')
p.card(1120,590,440,295,'Gemini API boundary',['gemini-3.5-flash (default)','Video extraction / planner / summary','Separate model grounding check','gemini-embedding-2 -> 768-d vectors','120 s call timeout; 1 transient retry','Small inline MP4: integration verified','URL + Files processing: HTTP 500','Live stream integration: not yet tested'],kind='model',code='google-genai + Pydantic',size=16)
p.line([(1055,744),(1120,744)]);p.text(1087,728,'API',12,MUTED,mono=True,anchor='middle')
p.tag(40,925,'TOOLS',BLUE)
p.card(40,948,315,163,'Inspect + validate',['Recorded windows <= 300 s','Video sampling: 1 fps','Finite timestamps; provenance','MP4 <= 12 MB inline; else Files','Live clips use capture offsets'],kind='model',size=15,title_size=20)
p.card(390,948,315,163,'Retrieve + filter',['Embed question; vector similarity','Strict start/end + availability','Top 30 + related claim conflicts','Retain coverage gaps / limitations','Stored notes are model evidence'],kind='app',size=15,title_size=20)
p.card(740,948,315,163,'Synthesize + check',['Narrative -> known evidence IDs','Gemini grounding Verification','Rejected output -> labelled extracts','Missing evidence -> clarification','No claim of guaranteed accuracy'],kind='model',size=15,title_size=20)
p.line([(355,1026),(390,1026)]);p.line([(705,1026),(740,1026)])
p.line([(200,885),(200,948)]);p.line([(550,885),(550,948)]);p.line([(900,885),(900,948)])
p.line([(40,470),(22,470),(22,1028),(40,1028)],color=RED,dash=True,marker='red')
p.card(1120,948,440,163,'Evidence store',['SQLite: evidence, windows, window_notes','JSON observations + normalized vectors','Reinspection replaces contained notes','Full interval and cutoff checks at retrieval','Written by inspect; read by retrieve'],size=16)
p.line([(550,1111),(550,1147),(1090,1147),(1090,1030),(1120,1030)],color=BLUE,marker='blue')
p.text(570,1137,'retrieval / indexed evidence',13,BLUE,mono=True)
p.card(40,1175,1015,133,'Cited recap -> durable human review',['interrupt() pauses for source verification; approve / reject records a decision.','UI calls Service.review() -> Command(resume=decision); thread_id = owner:job.','Result + evidence + trace export; clarification or failures can end without a recap.'],kind='human')
p.card(1120,1175,440,133,'Graph checkpoints',['SqliteSaver -> checkpoints.sqlite','Persists graph steps, not only approval','Resume is scoped to owner + job'])
p.line([(900,1111),(900,1175)],color=GREEN,marker='green');p.line([(1055,1240),(1120,1240)],color=GREEN,marker='green')
p.tag(40,1351,'SEPARATE SURFACES / these are not dependencies of a video recap')
p.card(40,1370,490,161,'Evidence demo + optional React',['TypeScript / Zod / LangGraph -> D1','VTT/SRT/JSON; lexical + hashed ranking','Byte-weighted LRU: 500 KB / 5 min','Revision-aware cache; manual live append'],kind='app',size=16)
p.card(555,1370,490,161,'Evaluation + specialization',['40 synthetic evidence cases; 20 -> 40 pass','BERT-tiny + PEFT LoRA: 52.5% -> 70%','Offline router; not deployed in this graph','Local traces; LangSmith quota blocked'],size=16)
p.card(1070,1370,490,161,'Prepared public deployment',['Docker + Caddy HTTPS + Google OIDC','Verified-email allow-list; persistent volume','Container / hosted login not validated','Local-first scope; no hosted service claimed'],kind='blocked',size=16)
p.footer(1560,'Solid arrows: primary calls / data relationships. Dashed arrows: conditional or fallback paths. Labels describe the implemented local design.','Validation status: 10 Sep 2026. Small-video integration is not real-race accuracy. Secrets and runtime data stay outside Git.')
p.save('racetime-system-architecture.svg')

p=Plate('II. How one video question runs','The actual recap graph: retrieve first, bound the decision, inspect when needed, then pause for review.',1780,'Decision flow for a RaceTime recap job. Retrieval feeds legal-action selection, Gemini or rules choose an action, inspection loops to retrieval, summary is checked then paused for human review, and clarification ends without a generated recap. Queue and budget failure paths are explicit.')
p.card(310,205,660,112,'0 / Worker claims an account-scoped recap',['media + question + start / end / as_of','SQLite lease + heartbeat; job status = running'],kind='app')
p.card(1040,205,520,112,'Input contract',['0 <= start < end <= as_of <= 604800 s','Interval <= 1 hour; valid owned media'],kind='app',size=16)
p.line([(640,317),(640,365)])
p.card(310,365,660,170,'1 / Retrieve existing observations',['Full containment + availability cutoff + source-text filter','Question embedding -> similarity-ranked vectors','Top 30 notes + related annotated conflicting claims','Update selected, retrieved, coverage, gaps and trace'],kind='app',code='Agent.retrieve() -> Store + Gemini.embed()')
p.card(1040,365,520,170,'Observation contract',['id / start / end / text / kind','runner / claimKey / claimValue (when known)','availableAt / provenance; persisted 768-d vector','No eligible observations = empty selection'],size=16)
p.line([(640,535),(640,585)])
p.card(310,585,660,143,'2 / Compute the permitted actions',['Cold recorded source with no notes -> inspect','Existing notes -> summarize; inspect may remain legal','Live with no usable notes -> clarify; never inspect old live','At the iteration cap -> summarize or clarify'],kind='app',size=16)
p.card(1040,585,520,143,'State constrains the planner',['retrieved / inspected / iterations / selected','Inspect is available only before its bounded use.','After inspect, retrieval runs again.','Rules choose directly when only one action is legal.'],kind='app',size=16)
p.line([(640,728),(640,790)])
p.card(310,790,660,155,'3 / Choose one action + record the reason',['Multiple choices: Gemini returns a structured Decision.','Validate action membership; accept only a permitted tool.','One choice: run the rule directly.','Record mode = llm / rule / fallback in trace.'],kind='model',size=17)
p.card(1040,790,520,155,'Planner unavailable / invalid response',['Use a permitted fallback:','summarize if possible, otherwise inspect, else clarify.','The same budgets and evidence boundaries apply.','Fallback is recorded, not presented as a model choice.'],kind='app',size=16)
p.line([(970,827),(1040,827)],dash=True);p.text(1002,811,'error',12,MUTED,mono=True,anchor='middle')
p.line([(1040,922),(1000,922),(1000,971),(640,971)],dash=True)
p.line([(640,945),(640,997)],arrow=False)
p.line([(640,997),(150,997),(150,1045)])
p.line([(640,997),(640,1045)])
p.line([(640,997),(1300,997),(1300,1045)])
p.tag(60,1027,'clarify',RED);p.tag(665,1027,'summarize',AMBER);p.tag(1320,1027,'inspect',AMBER)
p.card(40,1045,220,142,'Clarification',['Insufficient evidence.','Choose another interval','or clarify the question.','END; no review pause.'],kind='blocked',size=15,title_size=20)
p.card(310,1045,660,166,'4 / Generate a cited recap, then check it',['Gemini Narrative: at most 6 sentences, each with IDs.','Reject unknown IDs; Gemini Verification checks support.','Failure -> up to 6 labelled extracts + warning.','Both paths preserve the selected source observations.'],kind='model',code='Gemini.summarize() -> Agent.summarize()')
p.card(1040,1045,520,166,'Inspect the bounded recorded interval',['Source URI / inline MP4 / provider file','Extract observations -> validate time bounds','Embed text -> save window, notes + vectors','Set inspected = true -> retrieve again'],kind='model',code='Service.inspect(force=True)')
p.line([(1560,1120),(1582,1120),(1582,552),(995,552),(995,450),(970,450)],color=BLUE,marker='blue')
p.text(1190,546,'new evidence -> retrieve -> plan',14,BLUE,mono=True)
p.line([(640,1211),(640,1270)],color=GREEN,marker='green')
p.card(310,1270,660,170,'5 / Pause for human source review',['interrupt({ narrative }) persists the waiting graph.','Job becomes awaiting_review; UI displays citations.','The reviewer checks footage, then approves or rejects.','Saved state survives a worker / app restart.'],kind='human',code='SqliteSaver / checkpoints.sqlite')
p.card(1040,1270,520,170,'Failure and cancellation boundaries',['120 s model timeout; one retry on eligible errors','32 calls / job; 120 / account / 24 h (defaults)','Cancellation checked between processing operations','Uncaught processing failure -> failed job with safe error','Completed live windows survive interrupted capture'],kind='blocked',size=15)
p.line([(640,1440),(640,1497)],color=GREEN,marker='green')
p.card(310,1497,660,116,'6 / Resume and save the review decision',['Command(resume=approved | rejected), same owner:job','review stored -> completed -> source-linked JSON export'],kind='human')
p.card(1040,1497,520,116,'Meaning of completed',['The workflow finished and a decision was saved.','It does not certify the factual accuracy of the recap.'],size=16)
p.tag(40,1671,'READ THE TRACE: plan -> retrieve -> plan -> inspect (if needed) -> retrieve -> plan -> summarize -> human_review',BLUE)
p.footer(1685,'Live capture is a separate job; this recap graph can query only processed live observations. No active-stream test has been claimed.','This plate describes current code, not a hypothetical multi-agent design. Rules, model calls, fallback and review are intentionally distinct.')
p.save('racetime-decision-flow.svg')
print('Built two SVG plates in',OUT)
