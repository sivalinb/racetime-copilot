"""Offline contracts and real SQLite/LangGraph integration; no provider-quality claims."""
import json,tempfile,time,unittest,uuid,os
os.environ["LANGSMITH_TRACING"]="false"
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from racetime.store import Store
from racetime.agent import Agent
from racetime.provider import Gemini,Observations,Narrative
from racetime.service import Service,youtube,interval

class FakeProvider:
    def __init__(self,*_):pass
    def embed(self,texts,query=False):return [[1.0]+[0.0]*767 for _ in texts]
    def plan(self,q,actions,events,context=None):return {'action':'summarize' if events else 'inspect','reason':'Fixture planner choice.'}
    def summarize(self,q,events):return {'sentences':[{'text':events[0]['text'],'evidence_ids':[events[0]['id']]}]}

class ProductTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.store=Store(self.root/'db.sqlite');self.owner='owner';self.media='media'
        self.store.save_media(self.owner,{'id':self.media,'title':'Test fixture','url':'https://www.youtube.com/watch?v=qnVos4_1soM','path':'','duration':3600,'kind':'recorded'})
        self.query={'media':self.media,'start':0,'end':900,'as_of':900,'question':'What happened?'}
        self.job=self.store.enqueue(self.owner,'recap',self.query)
    def tearDown(self):self.tmp.cleanup()
    def events(self):
        events=[{'id':'a','start':20,'end':30,'text':'Commentary reports a runner at the checkpoint.','kind':'commentary','availableAt':30},{'id':'future','start':950,'end':970,'text':'Future result','kind':'timing','availableAt':970},{'id':'delayed','start':40,'end':50,'text':'Delayed result','kind':'timing','availableAt':999}]
        self.store.save_window(self.owner,self.media,0,1000,events,FakeProvider().embed(events))
    def agent(self,provider=None):return Agent(self.store,provider or FakeProvider(),self.owner,self.job,lambda *_:None,self.root/'checkpoints.sqlite')
    def test_account_survives_store_restart(self):
        self.store.register('runner','a long test password')
        owner=self.store.login('runner','a long test password')
        self.assertEqual(Store(self.store.path).login('runner','a long test password'),owner)
        with self.assertRaises(ValueError):self.store.login('runner','incorrect')
    def test_cross_account_isolation(self):
        for fn in [lambda:self.store.media('other',self.media),lambda:self.store.job('other',self.job),lambda:self.store.observations('other',self.media)]:
            with self.assertRaises(ValueError):fn()
    def test_durable_review_and_spoiler_filter(self):
        self.events();a=self.agent();result,waiting=a.run({**self.query,'trace':[]});a.close()
        self.assertTrue(waiting);self.assertEqual([e['id'] for e in result['selected']],['a'])
        b=self.agent();result,waiting=b.run(resume='approved');b.close()
        self.assertFalse(waiting);self.assertEqual(result['review'],'approved')
    def test_illegal_planner_action_falls_back(self):
        self.events();provider=FakeProvider()
        def bad(*_,**kwargs):raise ValueError('Planner chose an action outside its permitted set.')
        provider.plan=bad;a=self.agent(provider);r,_=a.run({**self.query,'trace':[]});a.close()
        self.assertTrue(any(t.get('mode')=='fallback' for t in r['trace']))
    def test_generated_summary_failure_keeps_evidence(self):
        self.events();provider=FakeProvider()
        def fail(*_):raise ValueError('Grounding check rejected the generated summary.')
        provider.summarize=fail;a=self.agent(provider);r,_=a.run({**self.query,'trace':[]});a.close()
        self.assertEqual(r['narrative']['sentences'][0]['evidence_ids'],['a']);self.assertIn('warning',r['narrative'])
    def test_live_missing_evidence_clarifies_without_inspect(self):
        m=self.store.media(self.owner,self.media);m['kind']='live';self.store.save_media(self.owner,m)
        a=self.agent();r,waiting=a.run({**self.query,'trace':[]});a.close();self.assertFalse(waiting);self.assertIn('clarification',r)
    def test_leases_recover_recorded_jobs(self):
        claimed=self.store.claim();self.assertEqual(claimed['id'],self.job)
        with self.store.db() as c:c.execute('UPDATE jobs SET lease=? WHERE id=?',(time.time()-1,self.job))
        self.assertEqual(self.store.claim()['attempts'],2)
    def test_live_job_never_restarts_with_stale_time_origin(self):
        self.store.finish(self.owner,self.job,'completed')
        id=self.store.enqueue(self.owner,'live',self.query);self.store.claim()
        with self.store.db() as c:c.execute('UPDATE jobs SET lease=? WHERE id=?',(time.time()-1,id))
        self.assertIsNone(self.store.claim());self.assertEqual(self.store.job(self.owner,id)['status'],'failed')
    def test_budget_is_reserved_before_call(self):
        with patch('racetime.store.MAX_CALLS',1):
            self.store.reserve(self.owner,self.job,'test')
            with self.assertRaises(ValueError):self.store.reserve(self.owner,self.job,'test')
    def test_cancel_queued_job(self):
        self.store.cancel(self.owner,self.job);self.assertIsNone(self.store.claim());self.assertEqual(self.store.job(self.owner,self.job)['status'],'cancelled')
    def test_url_and_interval_validation(self):
        self.assertEqual(youtube('https://youtu.be/qnVos4_1soM'),'https://www.youtube.com/watch?v=qnVos4_1soM')
        for u in ['http://localhost/','https://youtube.com.evil.test/watch?v=qnVos4_1soM','https://youtube.com/watch?v=x']:
            with self.assertRaises(ValueError):youtube(u)
        for values in [(0,30,20),(float('nan'),30,30),(0,4000,4000)]:
            with self.assertRaises(ValueError):interval(*values)
    def test_provider_timestamp_contract(self):
        g=Gemini(self.store,self.owner,self.job,client=object())
        g.call=lambda *_:Observations.model_validate({'events':[{'start':999,'end':1000,'text':'Outside','kind':'visual'}],'limitations':[]})
        with self.assertRaises(ValueError):g.extract('https://www.youtube.com/watch?v=qnVos4_1soM',0,30)
    def test_provider_unknown_citation_rejected(self):
        g=Gemini(self.store,self.owner,self.job,client=object())
        g.call=lambda *_:Narrative.model_validate({'sentences':[{'text':'Invented','evidence_ids':['missing']}]})
        with self.assertRaises(ValueError):g.summarize('What happened?',[{'id':'real','text':'Observed'}])
    def test_provider_error_is_sanitized(self):
        def fail(**_):raise RuntimeError('GEMINI_API_KEY=secret-test-marker')
        g=Gemini(self.store,self.owner,self.job,client=SimpleNamespace(models=SimpleNamespace(generate_content=fail)))
        with self.assertRaises(ValueError) as error:g.call('test','prompt',Narrative)
        self.assertNotIn('secret-test-marker',str(error.exception))
    def test_worker_runs_real_checkpoint_flow(self):
        self.events();svc=Service(self.store,FakeProvider)
        with patch('racetime.service.Agent',lambda *args:Agent(*args,checkpoint_path=self.root/'worker.sqlite')):
            self.assertTrue(svc.process_one());self.assertEqual(self.store.job(self.owner,self.job)['status'],'awaiting_review')
            svc.review(self.owner,self.job,'rejected');self.assertEqual(self.store.job(self.owner,self.job)['result']['review'],'rejected')

    def test_empty_recorded_source_is_inspected_before_clarification(self):
        calls=[]
        def inspect(*args):calls.append(args);self.events()
        a=Agent(self.store,FakeProvider(),self.owner,self.job,inspect,self.root/'cold.sqlite')
        r,waiting=a.run({**self.query,'trace':[]});a.close()
        self.assertEqual(len(calls),1);self.assertTrue(waiting);self.assertEqual(r['selected'][0]['id'],'a')
    def test_missing_coverage_and_provider_limits_are_visible(self):
        self.store.save_window(self.owner,self.media,0,100,[],[],['Audio unclear'])
        self.store.save_window(self.owner,self.media,200,300,[],[])
        r=self.store.coverage(self.owner,self.media,0,400)
        self.assertEqual(r['gaps'],[[100,200],[300,400]]);self.assertEqual(r['limitations'],['Audio unclear'])
    def test_reinspection_replaces_stale_observations(self):
        self.events();self.store.save_window(self.owner,self.media,0,1000,[],[])
        self.assertEqual(self.store.observations(self.owner,self.media),[])
    def test_fractional_interval_does_not_overinspect(self):
        calls=[]
        class Inspector(FakeProvider):
            def extract(self,uri,a,b):calls.append((a,b));return [],[]
        Service(self.store,Inspector).inspect(self.owner,self.job,self.media,0.5,601.1)
        self.assertEqual(calls,[(0.5,300.5),(300.5,600.5),(600.5,601.1)])
    def test_invalid_upload_is_removed(self):
        with patch('racetime.service.DATA',self.root),patch('racetime.service.duration',side_effect=ValueError('Invalid media')):
            with self.assertRaises(ValueError):Service(self.store).add_video(self.owner,'Bad video',upload=b'invalid',filename='test.mp4')
        self.assertEqual(list((self.root/'uploads'/self.owner).iterdir()),[])
    def test_json_schema_uses_supported_sdk_field(self):
        def generate(**kw):
            self.assertIsNone(kw['config'].response_schema)
            self.assertEqual(kw['config'].response_json_schema,Observations.model_json_schema())
            return SimpleNamespace(text='{"events":[],"limitations":[]}',usage_metadata=None)
        g=Gemini(self.store,self.owner,self.job,client=SimpleNamespace(models=SimpleNamespace(generate_content=generate)))
        self.assertEqual(g.call('schema test','prompt',Observations).events,[])

if __name__=='__main__':unittest.main(verbosity=2)
