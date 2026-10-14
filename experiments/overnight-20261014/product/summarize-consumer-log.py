from pathlib import Path
import collections,re,json,sys
rows={};groups=collections.Counter();r0=collections.Counter();phase=collections.Counter();masks={}
lines=Path(sys.argv[1]).read_text().splitlines()
fields=lambda line:dict(re.findall(r'(\w+)=(\S+)',line))
for line in lines:
 if line.startswith('PREFIX_SHOT phase=divide '):
  d=fields(line);rows[int(d['index'])]=d
 if line.startswith('PREFIX_STATE '):
  d=fields(line);masks[d['phase']]=int(d['phase_mask'],16)
for line in lines:
 if line.startswith('FINAL_CONSUMER_SHOT '):
  d=fields(line);before=rows[int(d['index'])]
  rep='literal0' if int(before['y'],16)==0 else 'p' if before['family']=='zero_slope' else 'nonzero'
  key=(d['family'],rep)
  groups[key,'shots']+=1
  for name in ['x_bad','y_bad','dirty','classical_input_changed']:
   groups[key,name]+=int(d[name]=='true')
  groups[key,'phase_bad']+=int(d['phase_bad'])
 if line.startswith('R0_SHOT '):
  d=fields(line);r0[(d['family'],d['delta'],d['extension_uniform'],d['odd'])]+=1
for name,mask in masks.items():
 for index,d in rows.items():
  rep='literal0' if int(d['y'],16)==0 else 'p' if d['family']=='zero_slope' else 'nonzero'
  phase[(name,d['family'],rep)]+=(mask>>index)&1
result=dict(final_family_counts={str(k):v for k,v in groups.items()},signed_r0_counts={str(k):v for k,v in r0.items()},phase_prefix_counts={str(k):v for k,v in phase.items()},qualified_score=None)
if len(sys.argv)>2:Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
