from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parent
dest=root/'source-t0-model';dest.mkdir(exist_ok=True)
s=(root/'walk_model.py').read_text();assert 'tick<=99' in s
s=s.replace('ROOT=Path(__file__).parent','from source_payload import seed_half_word, tick0_oneadd_word\n\nROOT=Path(__file__).parent')
needle='def onefold(a,b,signs,extra,tick,reverse=False):\n';assert s.count(needle)==1
s=s.replace(needle,needle+'    if tick==0 and not reverse:\n        return tick0_oneadd_word(a,b,signs,extra)\n')
needle='c=[1,half(1)] if payload is None else [payload,half(payload)]';assert s.count(needle)==1
s=s.replace(needle,'c=[1,half(1)] if payload is None else [payload,seed_half_word(payload)]')
(dest/'walk_model.py').write_text(s)
for name in ['predict-recovered.py','parallel-recovered.py','source_payload.py']:shutil.copy2(root/name,dest/name)
(dest/'model-source').mkdir(exist_ok=True)
for name in ['steps.txt','anchors.txt']:shutil.copy2(root/'model-source'/name,dest/'model-source'/name)
import sys
sys.path.insert(0,str(dest))
import walk_model as m
P=m.P;F=(1<<32)+977;fs=53
values=[0,1,2,F-1,F,F+1,(1<<fs)-1,(1<<fs)+1,P-1]
for i in [31,32,55,56,57,63,127,200,254,255]:values.extend([1<<i,(1<<i)-1])
rows=[]
for T in values:
 for bits in range(32):
  signs=[bits&1,(bits>>1)&1,(bits>>2)&1];extra=bits>>3
  S=m.seed_half_word(T);out=m.onefold(T,S,signs,extra,0)
  rows.append((T,bits,S,out))
(dest/'t0-boundaries.tsv').write_text(''.join(f'{i} '+ ' '.join(hex(v)for v in row)+'\n'for i,row in enumerate(rows)))
(dest/'source-contract.json').write_text(json.dumps(dict(source='4b2ec52f',forward_prefix_last_tick=99,seed_width=53,tick0='P3_T0_ONE_ADD',boundary_cases=len(rows),status='RESEARCH_MODEL_NOT_CERTIFIED_FOR_REJECTION'),indent=2)+'\n')
print('prepared separate exact-source-seed/T0 model',dest,'boundarycases',len(rows))
