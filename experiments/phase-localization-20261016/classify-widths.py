from pathlib import Path
import json,ast,bisect,collections
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016');assert(r/'source-v2-raw-verification.exit').read_text().strip()=='0'
comp=[];hmr={}
for line in(r/'source-v2-map.log').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='PHASE_CMP':comp.append(dict(at=int(f[1]),u=ast.literal_eval(f[2]),v=ast.literal_eval(f[3]),borrow=None if f[4]=='None'else int(f[4][5:-1]),context=ast.literal_eval(f[5].replace('true','True').replace('false','False'))))
 if f[0]=='PHASE_HMR':hmr[int(f[1])]=dict(q=int(f[2]),bit=int(f[3]),file=f[4],line=int(f[5]))
comp.sort(key=lambda c:c['at']);ats=[c['at']for c in comp];data=json.loads((r/'phase-sensitivity-classification.json').read_text());widths=collections.Counter();front=[]
for row in data['rows']:
 for hit in row['hits']:
  mapped=[]
  for raw in hit['raw_matches']:
   j=bisect.bisect_left(ats,raw+1);near=[c for c in comp[j:j+2]if c['at']<=raw+1000];mapped.append(dict(raw=raw,caller=hmr[raw],near_comparators=near))
  hit['v2_source_comparators']=mapped
  if mapped and mapped[0]['near_comparators']:widths[len(mapped[0]['near_comparators'][0]['u'])]+=1
  if any(m['caller']['file'].endswith('leapfrog.rs')and m['caller']['line']==3983 for m in mapped):front.append(dict(input_lane=row['input_lane'],witness=row['witness'],hit=hit))
out=dict(source_comparator_count=len(comp),static_width_counts=dict(collections.Counter(len(c['u'])for c in comp)),witness_first_comparator_widths=dict(widths),front_seam_witnesses=front,rows=data['rows'])
(r/'phase-width-classification.json').write_text(json.dumps(out,indent=2)+'\n');(r/'source-comparator-interfaces.json').write_text(json.dumps(comp,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k!='rows'},indent=2))
