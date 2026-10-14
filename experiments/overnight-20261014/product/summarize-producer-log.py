from pathlib import Path
import collections,re,json,sys
log=Path(sys.argv[1]).read_text().splitlines();f=lambda s:dict(re.findall(r'(\w+)=(\S+)',s));before={};groups=collections.Counter();words=collections.Counter()
for s in log:
 if s.startswith('PREFIX_SHOT phase=divide '):d=f(s);before[int(d['index'])]=d
for s in log:
 if not s.startswith('PRODUCER_SHOT '):continue
 d=f(s);b=before[int(d['index'])];rep='literal0' if int(b['y'],16)==0 else 'p' if b['family']=='zero_slope' else 'nonzero';key=(d['label'],d['family'],rep)
 groups[key,'shots']+=1
 groups[key,'product_bad']+=int(d['product_correct']=='false')
 groups[key,'phase_changed']+=int(d['phase_delta'])
 groups[key,'input_changed']+=int(d['input_restored']=='false')
 if d['label'].endswith('.producer'):words[(d['label'],d['family'],rep,d['product'],d['expected'],d['delta'])]+=1
result=dict(groups={str(k):v for k,v in groups.items()},words={str(k):v for k,v in words.items()},qualified_score=None)
if len(sys.argv)>2:Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
