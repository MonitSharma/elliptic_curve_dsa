exec((__import__('pathlib').Path(__file__).parent/'bind-carry-helpers.py').read_text().split('raw=load(')[0])
final=load(root.parent/'product-exact-20261015/tip/ops.bin');prior=json.loads((out/'opaque-closure-spans.json').read_text());start=5521782;rows=[]
ends=sorted({r['closure_end']for r in prior['selected']if 5522048<r['closure_end']<=start+100000})
for b in ends:
 depth=0;ok=True
 for i in range(start,b):
  k=struct.unpack_from('<Q',final,i*56)[0]
  if k==15:depth+=1
  if k==16:depth-=1
  if depth<0:ok=False;break
 if not ok or depth:continue
 rows.append(dict(final_begin=start,final_end=b,ops=b-start,criterion='from exact previous certified macro exit through source-anchored next complete square cleanup boundary',final_sha256=hashlib.sha256(final[start*56:b*56]).hexdigest()))
(out/'opaque-tail-v1-spans.json').write_text(json.dumps(dict(rows=rows,status='DIAGNOSTIC_CANDIDATES only; independent universal actual-final proof mandatory'),indent=2)+'\n')
(out/'opaque-tail-v1-proof-spans.tsv').write_text(''.join(f"{start}\t{r['final_end']}\t0\t0\n"for r in rows));print('TAIL_V1',[(r['final_begin'],r['final_end'],r['ops'])for r in rows])
