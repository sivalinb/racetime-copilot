"""Bounded planner with real durable LangGraph human interruption."""
import math, operator, re, sqlite3
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.sqlite import SqliteSaver
from .config import DATA

class State(TypedDict,total=False):
    question: str
    start: float
    end: float
    as_of: float
    media: str
    coverage: list
    gaps: list
    limitations: list
    selected: list
    action: str
    iterations: int
    retrieved: bool
    inspected: bool
    narrative: dict
    review: str
    clarification: str
    trace: Annotated[list,operator.add]

class Agent:
    def __init__(self,store,provider,owner,job,inspect,checkpoint_path=None):
        self.store,self.provider,self.owner,self.job,self.inspect=store,provider,owner,job,inspect
        self.connection=sqlite3.connect(checkpoint_path or DATA/'checkpoints.sqlite',check_same_thread=False)
        self.checkpointer=SqliteSaver(self.connection)
        graph=StateGraph(State)
        for name,fn in [('plan',self.plan),('retrieve',self.retrieve),('inspect',self.inspect_node),('summarize',self.summarize),('clarify',self.clarify),('review',self.review)]:graph.add_node(name,fn)
        graph.add_edge(START,'plan')
        graph.add_conditional_edges('plan',lambda s:s['action'],{'retrieve':'retrieve','inspect':'inspect','summarize':'summarize','clarify':'clarify'})
        graph.add_edge('retrieve','plan');graph.add_edge('inspect','retrieve');graph.add_edge('summarize','review');graph.add_edge('clarify',END);graph.add_edge('review',END)
        self.graph=graph.compile(checkpointer=self.checkpointer)
    def plan(self,s):
        if not s.get('retrieved'):actions=['retrieve']
        else:
            actions=['clarify']
            if s.get('selected'):actions.append('summarize')
            if not s.get('inspected') and s.get('iterations',0)<3 and self.store.media(self.owner,s['media'])['kind']!='live':actions.append('inspect')
        if s.get('retrieved') and not s.get('selected') and not s.get('inspected') and 'inspect' in actions:
            actions=['inspect']
        if s.get('iterations',0)>=4:actions=['summarize'] if s.get('selected') else ['clarify']
        if len(actions)==1:decision={'action':actions[0],'reason':'Only legal action for the current evidence and budget.'};mode='rule'
        else:
            try:decision=self.provider.plan(s['question'],actions,s.get('selected',[]),context={'start':s['start'],'end':s['end'],'source_available':True});mode='llm'
            except ValueError as exc:
                decision={'action':'summarize' if 'summarize' in actions else 'inspect' if 'inspect' in actions else 'clarify','reason':str(exc)};mode='fallback'
        return {'action':decision['action'],'iterations':s.get('iterations',0)+1,'trace':[{'step':'plan','mode':mode,**decision}]}
    def retrieve(self,s):
        pool=[(e,v) for e,v in self.store.observations(self.owner,s['media']) if s['start']<=e['start']<e['end']<=s['end'] and e.get('availableAt',e['end'])<=s['as_of'] and not re.search(r'ignore (?:all |previous |prior )?instructions|system prompt|reveal.*secret',e['text'],re.I)]
        if pool:
            q=self.provider.embed([s['question']],query=True)[0]
            scored=sorted(pool,key=lambda ev:sum(a*b for a,b in zip(q,ev[1],strict=True)),reverse=True)
            selected=[e for e,_ in scored[:30]]
            keys={e.get('claimKey') for e in selected if e.get('claimKey')}
            selected.extend(e for e,_ in pool if e.get('claimKey') in keys and e not in selected)
            selected.sort(key=lambda e:e['start'])
        else:selected=[]
        return {**self.store.coverage(self.owner,s['media'],s['start'],s['end']),'selected':selected,'retrieved':True,'trace':[{'step':'retrieve','mode':'semantic','count':len(selected)}]}
    def inspect_node(self,s):
        self.inspect(s['media'],s['start'],s['end'])
        return {'inspected':True,'trace':[{'step':'inspect','start':s['start'],'end':s['end']}]}
    def summarize(self,s):
        try:narrative=self.provider.summarize(s['question'],s['selected']);mode='generated_verified'
        except ValueError as exc:
            narrative={'sentences':[{'text':e['text'],'evidence_ids':[e['id']]} for e in s['selected'][:6]],'warning':str(exc)};mode='extractive_fallback'
        return {'narrative':narrative,'trace':[{'step':'summarize','mode':mode}]}
    def clarify(self,s):
        return {'clarification':'There is not enough usable evidence for this question. Choose another interval, make the question more specific, or inspect the video first.','trace':[{'step':'clarify','mode':'rule'}]}
    def review(self,s):
        decision=interrupt({'question':'Review the recap and timestamped evidence before approving.','narrative':s['narrative']})
        if decision not in ['approved','rejected']:raise ValueError('Choose approved or rejected.')
        return {'review':decision,'trace':[{'step':'human_review','decision':decision}]}
    def run(self,payload=None,resume=None):
        config={'configurable':{'thread_id':self.owner+':'+self.job},'recursion_limit':24,'run_name':'racetime-video-agent','metadata':{'job_id':self.job,'media_id':(payload or {}).get('media','')}}
        result=self.graph.invoke(Command(resume=resume) if resume else payload,config)
        result.pop('__interrupt__',None)
        waiting=bool(self.graph.get_state(config).next)
        return result,waiting
    def close(self):self.connection.close()
