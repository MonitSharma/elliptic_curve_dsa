from pathlib import Path
import json,re,sys
log=Path(sys.argv[1]);meta=Path(sys.argv[2]);cuts={};lines=[]
for line in log.read_text().splitlines():
 if line.startswith('PHASE_ANCHOR '):
  f=line.split();cuts[f[1]]=int(f[3])
 if line.startswith('PRODUCER_OBSERVE '):
  m=re.fullmatch(r'PRODUCER_OBSERVE (\S+) (\S+) (\d+) (\S+) (\[.*?\]) (\[.*?\])',line);assert m,line
  policy,stage,at,offset,x,p=m.groups();label=policy+'.'+stage
  cuts[label]=int(at);x=json.loads(x);p=json.loads(p)
  lines.append(' '.join([label,offset,','.join(map(str,x)),','.join(map(str,p))]))
meta.write_text('\n'.join(lines)+'\n')
print(','.join(k+':'+str(v) for k,v in sorted(cuts.items(),key=lambda item:item[1])))
