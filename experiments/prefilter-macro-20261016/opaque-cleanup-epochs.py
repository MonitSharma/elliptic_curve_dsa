exec((__import__('pathlib').Path(__file__).parent/'bind-carry-helpers.py').read_text().split('raw=load(')[0])
final=load(root.parent/'product-exact-20261015/tip/ops.bin');none=(1<<64)-1;stack=[];seen=set();epochs=[];start=5497988;end=5600000;rows=[]
for i in range(end):
 x=struct.unpack_from('<7Q',final,i*56);k,q2,q1,t,ct,cc,rt=x
 if i>=start:
  if k in(11,12)and t in[916,917,918]and cc==none and not stack:
   seen.add(t)
   if len(seen)==3:epochs.append(i+1);seen.clear()
 if k==15:stack.append((i,cc))
 if k==16:stack.pop()
for b in epochs:
 if b<=5498437:continue
 for a in[start,start+3]:
  depth=0;ok=True
  for i in range(a,b):
   k=struct.unpack_from('<Q',final,i*56)[0]
   if k==15:depth+=1
   if k==16:depth-=1
   if depth<0:ok=False;break
  if not ok or depth:continue
  rows.append(dict(final_begin=a,final_end=b,ops=b-a,criterion='actual final initial carry-scratch unconditional clear through complete cleanup epoch of q916,917,918; no input/packet dependence',final_sha256=hashlib.sha256(final[a*56:b*56]).hexdigest()))
(out/'opaque-cleanup-epoch-spans.json').write_text(json.dumps(dict(rows=rows,status='DIAGNOSTIC_CANDIDATES; actual-final arbitrary-input or explicit-prefix universal proof mandatory'),indent=2)+'\n')
(out/'opaque-cleanup-epoch-proof-spans.tsv').write_text(''.join(f"{r['final_begin']}\t{r['final_end']}\t0\t0\n"for r in rows))
print('CANDIDATES',len(rows),'FIRST',rows[:8],'LAST',rows[-1:])
