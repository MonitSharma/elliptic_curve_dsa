from pathlib import Path
from collections import Counter
import hashlib,json
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016')
counts={}
for path in sorted((root/'population').glob('counts-*.tsv')):
    for line in path.read_text().splitlines():
        r,t,w,*v=map(int,line.split());key=(r,t,w)
        counts[key]=[a+b for a,b in zip(counts.get(key,[0]*5),v)]
assert len(list((root/'population').glob('counts-*.tsv')))==7
events=[]
for path in sorted((root/'population').glob('events-*.tsv')):
    for line in path.read_text().splitlines():
        b,l,r,t,w,c,L,E,Nm,m,bad,first=map(int,line.split())
        events.append(dict(batch=b,lane=l,reverse=bool(r),tick=t,width=w,carry=c,L=L,E=E,Nm=Nm,digit=m,final_bad=bool(bad),first=bool(first)))
ranked=sorted(counts.items(),key=lambda kv:(-kv[1][0],kv[0]))
table=[dict(reverse=bool(r),tick=t,width=w,events=n,positive=p,negative=m,final_bad=b,first_event=first) for(r,t,w),(n,p,m,b,first)in ranked]
data=dict(source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',inputs=262144,input_file='../prefilter-20261015/evidence/census-coordinates4096.tsv',input_sha256=hashlib.sha256((root.parent/'prefilter-20261015/evidence/census-coordinates4096.tsv').read_bytes()).hexdigest(),observation='actual production-body fold wires before postpasses, generator final-stream hash verified',scope='research census only; not resource score; not official nonce packet',events=len(events),event_inputs=len({(e['batch'],e['lane'])for e in events}),event_bad_inputs=len({(e['batch'],e['lane'])for e in events if e['final_bad']}),fold_sites=table)
(root/'fold-risk-summary.json').write_text(json.dumps(data,indent=2)+'\n')
(root/'fold-events.jsonl').write_text(''.join(json.dumps(e)+'\n'for e in sorted(events,key=lambda e:(e['batch'],e['lane'],not e['reverse'],e['tick']))))
# This declaration precedes building any precision candidate. All selected ticks
# are applied to every input. No official scored or nonce packet is consulted.
family=dict(name='one-extra-bit-by-broad-census-fold-risk',source_revision=data['source_revision'],training_inputs_sha256=data['input_sha256'],ranking='descending actual carry-drop count; ties forward before reverse then ascending tick',eligible='all actual production fold sites with nonzero observed signed carry drop',sizes=[1,4,8,16],change='increase fold precision by exactly one bit at every selected direction/tick for all inputs',maximum_sites=16,anchor_policy='all existing source-bound optimization tables and assertions retained exactly; rejection preserved without bypass',validation='any complete generated circuit must receive a fresh independent paired census before claims or search',ranked_sites=[dict(reverse=bool(r),tick=t,width=w,events=v[0])for(r,t,w),v in ranked])
(root/'PREDECLARED-FAMILY.json').write_text(json.dumps(family,indent=2)+'\n')
print(json.dumps(data,indent=2))
