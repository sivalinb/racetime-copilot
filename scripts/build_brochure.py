"""Build the 15-page RaceTime pitch, using measured repository reports."""
import json, sys
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'docs/RaceTime-Copilot-Brochure.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
W,H=792,612
INK='#20263e';BLUE='#303aa0';TEAL='#087b7b';MUTED='#526077';LINE='#d8e1ed';PALE='#eef2ff'
c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('RaceTime Copilot - Product, technology and capstone evidence');c.setAuthor('Siva Babu')
E=json.loads((ROOT/'reports/workflow-evaluation.json').read_text());R=json.loads((ROOT/'reports/router-evaluation.json').read_text())
page=0

def text(txt,x,y,w,size=11,color=INK,bold=False):
 p=Paragraph(txt,ParagraphStyle('p',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=size*1.34,textColor=HexColor(color),spaceAfter=0));_,h=p.wrap(w,1000);p.drawOn(c,x,H-y-h);return h

def box(x,y,w,h,color=PALE):
 c.setFillColor(HexColor(color));c.roundRect(x,H-y-h,w,h,10,fill=1,stroke=0)

def start(section,title,subtitle):
 global page
 page+=1;c.setFillColor(white);c.rect(0,0,W,H,fill=1,stroke=0)
 text('RACETIME / COPILOT',42,25,230,10,BLUE,True)
 text('Story     Workflow     Data     Learning     Results     Pilot',325,26,430,8,MUTED)
 c.setStrokeColor(HexColor(LINE));c.line(42,H-48,750,H-48)
 text(section.upper(),42,66,700,9,TEAL,True);text(title,42,86,708,27,INK,True);text(subtitle,42,128,708,11,MUTED)

def end():
 c.setStrokeColor(HexColor(LINE));c.line(42,43,750,43)
 text('RESEARCH PROTOTYPE / Evidence mode / 10 SEP 2026',42,577,510,8,MUTED)
 text(f'{page:02d} / 15',700,577,55,8,MUTED,True);c.showPage()

def art(name,y=169,h=275):
 path=ROOT/'public/art'/f'{name}.png';im=ImageReader(str(path));iw,ih=im.getSize();scale=min(708/iw,h/ih);ww,hh=iw*scale,ih*scale;c.drawImage(im,42+(708-ww)/2,H-y-hh,ww,hh,mask='auto')

def cards(items,y=452,h=96):
 gap=14;w=(708-gap*(len(items)-1))/len(items)
 for i,(title,body) in enumerate(items):
  x=42+i*(w+gap);box(x,y,w,h,'#eef2ff' if i%2==0 else '#e9f5f2');text(title,x+14,y+12,w-28,11,BLUE,True);text(body,x+14,y+34,w-28,10)

def rows(items,y=180,widths=(132,275,301),rh=65):
 x=42
 for i,(a,b,d) in enumerate(items):
  yy=y+i*rh;box(42,yy,708,rh-5,'#f0f3fa' if i%2==0 else '#f7f9fc');off=42
  for j,v in enumerate([a,b,d]):text(v,off+12,yy+12,widths[j]-24,10,BLUE if j==0 else INK,j==0);off+=widths[j]

start('The product','A race story, on your clock.','Ask what happened in any available video interval. Rejoin the race with timestamped evidence.');art('overview',160,280)
cards([('The unmet need','Long broadcasts make a short absence expensive to reconstruct.'),('The product promise','A bounded catch-up with runner context, uncertainty and source links.'),('Working today','Transcript imports and extractive recaps; Gemini video analysis is deferred.')]);end()
start('Problem / solution','You missed 15 minutes. Not the whole race.','A viewer should not have to scrub hours of footage to rebuild a few meaningful moments.');art('workflow',168,248)
cards([('Before','Scrub the timeline, guess which runner is shown, reconcile stale graphics and risk future spoilers.'),('After','Choose a window. Retrieve eligible evidence. See contradictions, inspect timestamps and review the recap.')],434,112);end()
start('Who benefits','Built for people who follow the race.','Start with engaged fans and crews; expand to organizers and broadcast teams after a measured pilot.');art('audience',166,270)
cards([('Fans + families','Catch up on a runner or a missed interval without jumping ahead.'),('Crews + organizers','Find reported sightings and timing context, with uncertainty visible.'),('Broadcast editors','Locate candidate moments and evidence links for editorial review.')]);end()
start('How it works','Choose. Retrieve. Verify. Review.','A stateful evidence workflow supports the future multimodal agent. Today, facts come from imported observations.');art('workflow',165,270)
cards([('Working flow','Input validation -> intent route -> bounded retrieval -> one failure retry -> related-claim check -> extractive recap -> saved review.'),('Human checkpoint','Approval or rejection persists with the run. Export is a user action; no recap is automatically posted to an audience.')]);end()
start('Data / provenance','The source must tell its own story.','Every observation carries elapsed start/end times, a source type and a clear origin.');rows([
('Fictional replay','Canyon Relay and its runners are authored demo fixtures.','Useful for repeatable conflict, cutoff and retrieval tests. No real race result is asserted.'),
('User import','VTT/SRT captions or JSON timing/visual observations.','Source URL links to playback. Imported coverage is explicit; gaps can remain within it.'),
('Live evidence','Append new observations to an imported live source.','Optimistic revision checks prevent stale writes. A new revision invalidates old recap-cache keys.'),
('Deferred video','Gemini may extract bounded audio/visual observations.','Not connected or tested here. A pasted YouTube URL alone currently provides no evidence.')],175,rh=79);end()
start('Technology / purpose','Every technology earns a product job.','The architecture favors inspectable evidence and a small, reproducible local demo.');rows([
('React + TypeScript','Source picker, interval controls, import, recap and review.','Typed contracts keep client/server expectations aligned. shadcn primitives supply accessible UI controls.'),
('Zod + D1','Validate timestamps and persist sources, evidence and runs.','Parameterized SQL and browser-session scoping separate local workspaces; this is not production account auth.'),
('Retrieval + cache','BM25-style scores + hashed vectors; byte-weighted LRU.','Time/cutoff filters precede ranking. Cache keys include source revision and exact query.'),
('LangGraph','State, conditional retry and corroborating-claim inspection.','Visible trace stages explain what ran. The current orchestration is deterministic, not autonomous LLM reasoning.'),
('PyTorch + PEFT','Small LoRA experiment for recap/runner/verify/compare routing.','A held-out comparison and merge smoke test justify whether specialization helps.')],173,rh=74);end()
start('Week 5 / specialization','Measure the adapter. Then decide.','A practical routing experiment adapts the Week 5 technique to race-viewer intents.');
base=R['results']['frozen_encoder'];lora=R['results']['lora']
for i,(label,value,color) in enumerate([('Frozen encoder + trained head',base['accuracy'],BLUE),('LoRA + equally trained head',lora['accuracy'],TEAL)]):
 yy=188+i*95;text(label,42,yy,350,12,INK,True);box(42,yy+29,480,27,'#eef1f6');c.setFillColor(HexColor(color));c.roundRect(42,H-(yy+29)-27,480*value,27,5,fill=1,stroke=0);text(f'{value:.1%} accuracy',548,yy+30,195,15,color,True)
text('144 training examples / 40 held-out requests / 4 classes / seed 42 / rank 8',42,384,708,11,BLUE,True)
text(f'Macro F1: {base["macro_f1"]:.3f} -> {lora["macro_f1"]:.3f}. Adapter merge preserved logits within 1e-5 tolerance.',42,410,708,11)
cards([('Honest scope','BERT-tiny encoder classifier, not a generative LLM. The exact Qwen3 / LLaMA Factory workflow remains an extension.'),('Deployment decision','70% on a small synthetic holdout is insufficient for a reliable product router. The app keeps its inspectable rule router.')],452,96);end()
start('Measured results','A demo with evidence behind it.','Local automated results measure temporal and evidence handling, not real-world race-summary quality.');
metrics=[('17 / 17','Unit tests'),(f'{E["passed"]} / {E["count"]}','Synthetic evidence cases'),('Passed','API integration workflow')]
for i,(value,label) in enumerate(metrics):
 x=42+i*241;box(x,180,226,110);text(value,x+18,200,190,30,BLUE,True);text(label,x+18,249,190,11)
text('Baseline -> bounded workflow',42,320,708,17,INK,True)
text(f'Naive overlap retrieval: {E["baselinePassed"]}/40. Strict interval containment, availability cutoff and instruction filtering: {E["passed"]}/40.',42,351,708,12)
text(f'Local in-process latency: p50 {E["p50Ms"]:.1f} ms; p95 {E["p95Ms"]:.1f} ms. Provider calls: 0. These timings exclude network/UI latency.',42,395,708,11,MUTED)
cards([('Integration evidence','Import -> recap -> cross-session isolation -> review -> live append -> revision conflict -> persisted history.'),('Remaining validation','Independent review of the 40 cases, real transcript/video quality, external LangSmith traces and pilot usefulness.')],451,98);end()
start('Roadmap','From catch-up tool to race intelligence.','Sequence the expansion around evidence quality and user value, rather than adding agents for their own sake.');rows([
('Next milestone','Connect bounded Gemini video observations.','Validate timestamps and uncertain runner identity; compare against a human-reviewed video interval set.'),
('Race operations','Join official timing feeds and course checkpoints.','Align stream time, event time and delayed updates. Keep observed vs official facts distinct.'),
('Personal channels','Runner watchlists and accessible catch-up formats.','Multilingual narration, audio-only recaps and topic-specific updates need quality evaluation.'),
('Broadcast platform','Multi-camera moments and editor review queues.','Rights-aware clip suggestions, source-linked stories and a measurable production pilot.')],178,rh=78);end()
start('Explore / reproduce','One repository. A simple starting point.','Run the supported workflow without an API key. Reproduce the tests and inspect the reports.');
box(42,180,708,95);text('github.com/sivalinb/racetime-copilot',60,201,670,20,BLUE,True);text('npm ci  |  npm run dev  |  open localhost:3000',60,239,670,12)
c.linkURL('https://github.com/sivalinb/racetime-copilot',(42,H-275,750,H-180),relative=0)
rows([('README','Short setup + demo walkthrough.','Import supported evidence, select a range, review the result.'),('docs/','Technology map, architecture and demo guide.','Clear implementation status and remaining course-tool gaps.'),('reports/ + training/','40-case evaluation, LoRA comparison and merge smoke test.','Runnable scripts and authored datasets support the reported numbers.')],299,rh=79);end()
start('Sources / attribution','Keep the claims traceable.','Course handouts informed the learning map. Official documentation informed the architecture and future integration plan.');
refs=[('Course learning scope','User-provided Week 1-5 Project Handouts (August 2026); adapted capstone mapping, not an assertion of exact assignment completion.'),('Reference design','User-provided UltraMedia-Brochure.pdf: 15-page landscape narrative, top navigation, illustrations, explanation cards and readiness pages.'),('Workflow orchestration','LangGraph overview: docs.langchain.com/oss/javascript/langgraph/overview'),('Fine tuning','Hugging Face PEFT LoRA documentation: huggingface.co/docs/peft/en/developer_guides/lora; base model prajjwal1/bert-tiny.'),('Future video analysis','Google Gemini video understanding: ai.google.dev/gemini-api/docs/video-understanding. Provider access and selected-video support must be tested.'),('Product evidence','Repository reports/workflow-evaluation.json, router-evaluation.json and router-smoke.json; authored synthetic fixtures; 10 Sep 2026.')]
for i,(a,b) in enumerate(refs):text(a,42,174+i*61,190,11,BLUE,True);text(b,234,174+i*61,516,10)
end()
start('Readiness / learning coverage','A working foundation. Visible gaps.','The project spans all five themes. Several provider-specific and human-review requirements still need completion.');rows([
('Week 1','Working data app and iterative implementation.','Verified: browser controls, API workflows, persistence and review.'),
('Week 2','Ingestion, chunk-level retrieval, citations, refusal and freshness.','Verified locally. Hashed vectors are not learned embeddings; multimodal/LLM synthesis is deferred.'),
('Week 3','State, tools, branching, retry and human checkpoint.','Verified LangGraph execution and stored review; model-driven planning and durable graph resumption are future work.'),
('Week 4','40 cases, baseline delta, local traces and latency.','Verified synthetic suite. Independent labels and external LangSmith trace evidence remain pending.'),
('Week 5','LoRA training, held-out metrics, merge and inference smoke.','Verified adapted BERT experiment. Exact Qwen3-1.7B / LLaMA Factory parity is not claimed.')],174,rh=74);end()
start('A concrete case','Two reports disagree. The recap says so.','Illustrative Canyon Relay replay only. These are not claims about a real athlete or race.');
rows([('08:00 / E05','Commentary reports Lena Ortiz took the lead.','This is explicitly an unconfirmed broadcast claim.'),('08:10 / E06','The visible ridge graphic still lists Maya Chen first.','No visible update timestamp; this could be a stale graphic.'),('15:30 / E09','A later timing update confirms Maya at the checkpoint.','Excluded from a 00:00-15:00 recap. It is available in the later interval.')],179,rh=85)
cards([('What the user sees','Both early reports, their evidence IDs and a needs-review status. No inferred official position.'),('Why it matters','The system preserves uncertainty and the requested time boundary instead of silently using future knowledge.')],460,87);end()
start('The workbench','A product you can walk through.','Interface map for the implemented app. This diagram is an explanation of the UI, not a screenshot.');
box(42,176,300,352,'#f1f4fa');box(356,176,394,352,'#eef7f4')
text('01 / CHOOSE YOUR WINDOW',60,194,266,12,BLUE,True)
for i,(a,b) in enumerate([('Source','Canyon Relay / fictional replay'),('Interval','00:00 -> 15:00'),('Spoiler cutoff','15:00'),('Question','What happened?'),('Runner','Optional filter')]):
 text(a,60,233+i*48,250,9,MUTED,True);text(b,60,249+i*48,250,11)
box(60,485,264,29,BLUE);text('CREATE MY RECAP',72,492,240,10,'#ffffff',True)
text('02 / FOLLOW THE EVIDENCE',374,194,355,12,TEAL,True);text('NEEDS REVIEW',374,229,350,15,TEAL,True)
text('08:00 / commentary / E05',374,270,350,11,BLUE,True);text('Unconfirmed report: Lena takes the lead.',374,291,350,11)
text('08:10 / visual / E06',374,330,350,11,BLUE,True);text('Graphic still lists Maya. Timestamp unknown.',374,351,350,11)
text('Reports disagree. Inspect the source.',374,397,350,13,INK,True);text('Approve or reject / Export JSON / Inspect trace',374,450,350,11)
end()
start('Pilot brief / why this builder','A personal problem. An architectural story.','Endurance racing supplies the user insight. Observability and systems design supply the engineering discipline.');
rows([('Founder fit','Ultramarathoner, race organizer and livestream viewer.','Understands the questions fans and crews actually ask during long broadcasts.'),('Professional fit','Observability, infrastructure and customer architecture.','Time-bounded evidence, cache invalidation, traceable failures and explicit operating limits make an interview-ready systems discussion.'),('Pilot hypothesis','A fan can answer a missed-interval question faster.','Test five real users on three reviewed intervals; compare manual scrubbing with assisted catch-up. No benefit is claimed before this test.'),('Success + extension','Track completion time, evidence accuracy and trust.','Target zero spoiler leaks in the pilot; collect confusion and corrections before connecting automatic live ingestion.')],178,rh=78)
end();c.save();print(OUT)
