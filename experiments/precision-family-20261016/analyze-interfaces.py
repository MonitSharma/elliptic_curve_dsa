exec((__import__('pathlib').Path(__file__).parent/'analyze-isolated.py').read_text().split('rows=[]')[0])
from functools import lru_cache
final=load(root.parent/'product-exact-20261015/tip/ops.bin');full=list(struct.iter_unpack('<7Q',final));analysis=json.loads((root/'isolated-analysis.json').read_text());originals={r['tick']:r for r in family['records']};one=frozenset({frozenset()});zero=frozenset()
def atom(key):return frozenset({frozenset({key})})
def xor(a,b):return a^b
def mul(a,b):
 out=set()
 for x in a:
  for y in b:
   z=x|y
   if z in out:out.remove(z)
   else:out.add(z)
   if len(out)>200000:raise OverflowError('classical ANF limit')
 return frozenset(out)
def classify_liveness(end,bits):
 pending=set(bits);live={};depth=0
 for i in range(end,len(full)):
  k,a,b,t,bt,cc,rt=full[i]
  reads=({cc}if cc!=none else set())|({bt}if k==3 else set())
  for wire in pending&reads:live[wire]=dict(live_out=True,first_external_read=i,kind=k)
  pending-=reads
  if depth==0 and cc==none and k in[4,5,12]:
   for wire in pending&{bt}:live[wire]=dict(live_out=False,unconditional_overwrite=i,kind=k)
   pending.discard(bt)
  if k==15:depth+=1
  if k==16:depth-=1
  if not pending:break
 for wire in pending:live[wire]=dict(live_out=False,never_read_before_end=True)
 return live
def symbolic_classical(ops,cp,cs,which):
 b={};base=one;stack=[]
 get=lambda wire:b.get(wire,atom(('input',wire)))
 for i,(k,a,u,t,bt,cc,rt)in enumerate(ops):
  condition=base if cc==none else mul(base,get(cc))
  if k==15:stack.append(base);base=condition
  elif k==16:base=stack.pop()
  elif k in[3,4,5,12]:
   old=get(bt)
   if k==3:b[bt]=xor(old,condition)
   else:
    if k==4:value=zero
    elif k==5:value=one
    else:
     label=('prefix',i)if i<cp else('suffix',len(ops)-1-i)if i>=len(ops)-cs else(which,i)
     value=atom(label)
    b[bt]=xor(old,mul(condition,xor(old,value)))
 assert not stack
 return b
rows=[]
for r in analysis['rows']:
 if r['rejected']:continue
 t=r['tick'];aa=list(struct.iter_unpack('<7Q',load(d/f'tick-{t}.old.bin')));bb=list(struct.iter_unpack('<7Q',load(d/f'tick-{t}.new.bin')));cs=0
 for x,y in zip(reversed(aa),reversed(bb)):
  if x!=y:break
  cs+=1
 cs=min(cs,len(aa)-r['common_prefix']);old=symbolic_classical(aa,r['common_prefix'],cs,'old');new=symbolic_classical(bb,r['common_prefix'],cs,'new');bits=set(r['old']['bits_written']);assert bits==set(r['new']['bits_written'])
 live=classify_liveness(originals[t]['final_end'],bits);checks={wire:dict(**live[wire],equal_under_shared_prefix_suffix_mr=old[wire]==new[wire],old_terms=len(old[wire]),new_terms=len(new[wire]))for wire in bits};admitted=all(not x['live_out']or x['equal_under_shared_prefix_suffix_mr']for x in checks.values())
 rows.append(dict(tick=t,admitted_classical_interface=admitted,common_prefix=r['common_prefix'],common_suffix=cs,checks=checks,extra_scratch=r['added_scratch'],external_esh_equal=r['external_esh_equal']))
result=dict(rows=rows,admitted=sum(r['admitted_classical_interface']for r in rows),total=len(rows),method='exact classical ANF; arbitrary incoming bits, all internal HMR independent except identical prefix/suffix gate roles; dead final versions proven overwritten before any external read',component_only=True)
(root/'interface-analysis.json').write_text(json.dumps(result,indent=2)+'\n');print('INTERFACES',result['admitted'],result['total']);print('ROWS',[(r['tick'],r['admitted_classical_interface'],r['common_suffix'],r['checks'])for r in rows])
