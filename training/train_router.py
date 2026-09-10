"""Reproducible, small LoRA experiment; no video understanding is claimed.
Compare equally trained classifier heads: frozen encoder vs LoRA encoder.
Authored synthetic data, template-disjoint test set; not a real-user benchmark.
"""
import json, random, time, hashlib
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, BertForSequenceClassification, BertConfig
from peft import LoraConfig, get_peft_model, TaskType
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, confusion_matrix
ROOT=Path(__file__).resolve().parent
MODEL='prajjwal1/bert-tiny'
LABELS=['recap','runner','verify','compare']
SEED=42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
torch.set_num_threads(4)
subjects=['the canyon checkpoint','the ridge climb','the forest section','the finish area','the aid station','this interval']
patterns={
'recap':['Summarize what happened at {}.','Give me a recap of {}.','Catch me up on {}.','What were the key moments around {}?','Provide an overview of {}.','Tell me the story of {}.'],
'runner':['Follow Maya Chen around {}.','Where is runner Lena Ortiz at {}?','Track bib 214 near {}.','Show Maya Chen observations from {}.','Find updates for runner Lena at {}.','Which clips show bib 214 at {}?'],
'verify':['Verify the lead report at {}.','Do the reports conflict at {}?','Check whether the timing claim at {} is true.','Can you confirm the commentary from {}?','Is the reported gap at {} supported?','Investigate conflicting evidence around {}.'],
'compare':['Compare the reports from {}.','What is the difference between Maya and Lena at {}?','Contrast the two camera reports near {}.','Compare timing versus commentary at {}.','How do the two runners differ around {}?','Show a side-by-side comparison of {}.']}
train=[{'text':p.format(s),'label':label,'split':'train'} for label,ps in patterns.items() for p in ps for s in subjects]
tests={
'recap':['What happened in these fifteen minutes?','Give me the highlights since the broadcast returned.','I stepped away; what did I miss?','Brief me on the selected video window.','Explain the sequence of events in this range.','What should I know before rejoining the stream?','Make a chronological catch-up for this section.','List the important moments from minute ten to twenty.','Can I get a short race summary?','Recap the last part of the broadcast.'],
'runner':['Any news about bib 42?','Find shots featuring Maya Chen.','Where did Lena last appear?','Only include updates about runner Maya.','Track bib 87 through the available footage.','I am crewing for Lena; show her sightings.','Tell me where runner Chen was seen.','Filter this clip for bib 214.','Follow Lena rather than the whole field.','Show the most recent mention of runner Maya.'],
'verify':['Did that lead change actually happen?','The announcer and timing board disagree; which claims conflict?','Is the claimed arrival time backed by evidence?','Can we trust that gap announcement?','Check this claim against the visible timing.','Are the two position reports consistent?','Flag statements that cannot be confirmed.','Was the leader call supported at that moment?','Do we have corroboration for this report?','Verify whether the graphic contradicts the commentary.'],
'compare':['How did the first half differ from the second?','Contrast Lena with Maya over this interval.','Compare the earlier checkpoint with the later one.','What differs between the visual and spoken accounts?','Put the two reports next to each other.','Which changes stand out across both windows?','Give me the differences between these runners.','Show timing and commentary side by side.','Compare those two race sections.','How does this segment compare with the previous one?']}
heldout=[{'text':t,'label':l,'split':'test'} for l,ts in tests.items() for t in ts]
ROOT.mkdir(exist_ok=True)
(ROOT/'dataset.json').write_text(json.dumps({'provenance':'Author-created synthetic routing requests. Test wording authored separately from training templates. No external race data.','train':train,'test':heldout},indent=2))
cache=ROOT/'cache';cache.mkdir(exist_ok=True)
tok=AutoTokenizer.from_pretrained("google-bert/bert-base-uncased",cache_dir=cache)
X=tok([x['text'] for x in train],padding=True,truncation=True,max_length=64,return_tensors='pt');Y=torch.tensor([LABELS.index(x['label']) for x in train])
T=tok([x['text'] for x in heldout],padding=True,truncation=True,max_length=64,return_tensors='pt');TY=[LABELS.index(x['label']) for x in heldout]
results={}; predictions={}
for mode in ['frozen_encoder','lora']:
 torch.manual_seed(SEED)
 model=BertForSequenceClassification.from_pretrained(MODEL,config=BertConfig.from_pretrained(MODEL,num_labels=4,cache_dir=cache),cache_dir=cache)
 for p in model.parameters():p.requires_grad=False
 for p in model.classifier.parameters():p.requires_grad=True
 if mode=='lora':model=get_peft_model(model,LoraConfig(task_type=TaskType.SEQ_CLS,r=8,lora_alpha=16,lora_dropout=0.05,target_modules=['query','value'],modules_to_save=['classifier']))
 optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=0.002)
 started=time.monotonic();losses=[];model.train()
 for epoch in range(16):
  order=torch.randperm(len(Y),generator=torch.Generator().manual_seed(SEED+epoch))
  for ids in order.split(24):
   optimizer.zero_grad();out=model(**{k:v[ids] for k,v in X.items()},labels=Y[ids]);out.loss.backward();optimizer.step();losses.append(float(out.loss.detach()))
 model.eval()
 with torch.no_grad():pred=model(**T).logits.argmax(-1).tolist()
 precision,recall,f1,_=precision_recall_fscore_support(TY,pred,labels=list(range(4)),zero_division=0)
 results[mode]={'accuracy':accuracy_score(TY,pred),'macro_f1':f1_score(TY,pred,average='macro'),'precision_by_label':dict(zip(LABELS,precision.tolist())),'recall_by_label':dict(zip(LABELS,recall.tolist())),'f1_by_label':dict(zip(LABELS,f1.tolist())),'confusion_matrix':confusion_matrix(TY,pred,labels=list(range(4))).tolist(),'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad),'train_seconds':round(time.monotonic()-started,3),'initial_loss':losses[0],'final_loss':losses[-1],'steps':len(losses)}
 predictions[mode]=[{'text':x['text'],'expected':x['label'],'predicted':LABELS[y]} for x,y in zip(heldout,pred)]
 if mode=='lora':model.save_pretrained(ROOT/'checkpoints'/'adapter');tok.save_pretrained(ROOT/'checkpoints'/'adapter')
 print(mode,json.dumps(results[mode]),flush=True)
report={'model':MODEL,'base_revision':getattr(model.config,'_commit_hash',None),'seed':SEED,'labels':LABELS,'train_count':len(train),'test_count':len(heldout),'comparison':'Identical frozen pretrained encoder and classifier initialization; classifier trained in both arms. LoRA arm additionally trains rank-8 query/value adapters. Same data, batches, epochs and optimizer learning rate.','limitations':['Small authored synthetic dataset; no independent human review.','One seed, one split; no significance or real-user generalization claim.','Encoder classifier experiment, not a generative LLM or video model.','No deployment decision was made using training accuracy.'], 'results':results,'predictions':predictions,'dataset_sha256':hashlib.sha256((ROOT/'dataset.json').read_bytes()).hexdigest()}
(ROOT.parent/'reports'/'router-evaluation.json').write_text(json.dumps(report,indent=2))
