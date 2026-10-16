exec((__import__('pathlib').Path(__file__).parent/'bind-carry-helpers.py').read_text().split('raw=load(')[0])
final=load(root.parent/'product-exact-20261015/tip/ops.bin');none=(1<<64)-1;start=5495000;end=5503000;qs={962,963,964,965,966,916,917,918};bits={1649,1650,1651,1652,1653,1654};stack=[];rows=[]
for i in range(end):
 x=struct.unpack_from('<7Q',final,i*56);k,q2,q1,t,ct,cc,rt=x
 if i>=start and(t in qs or q1 in qs or q2 in qs or ct in bits):
  rows.append(dict(at=i,record=tuple(-1 if v==none else v for v in x),scope=list(stack)))
 if k==15:stack.append((i,cc))
 if k==16:stack.pop()
(out/'opaque-wire-trace.json').write_text(json.dumps(rows,indent=2)+'\n')
with(out/'opaque-wire-trace.txt').open('w')as f:
 for r in rows:print(r['at'],r['record'],'S',r['scope'],file=f)
for q in sorted(qs):
 rr=[r for r in rows if r['record'][3]==q and r['record'][0]in(6,8,10,11,12,13)]
 print('WRITES',q,[(r['at'],r['record'],len(r['scope']))for r in rr])
for b in sorted(bits):print('BITDEFS',b,[(r['at'],r['record'],len(r['scope']))for r in rows if r['record'][4]==b])
