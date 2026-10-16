exec((__import__('pathlib').Path(__file__).parent/'map-residual-sites.py').read_text().split('raw=load(')[0])
final=load(root.parent/'product-exact-20261015/tip/ops.bin')
d=json.loads((out/'opaque-inherited-table.json').read_text())
with(out/'opaque-helper-readable.txt').open('w')as f:
 for r in d['matches']:
  print('TABLE',r['table'],r['input_at'],r['row_offset'],file=f)
  for i,x in enumerate(r['rows']):print(i,x,file=f)
 for i in range(5498330,5498520):
  x=struct.unpack_from('<7Q',final,i*56);print('FINAL',i,tuple(-1 if v==none else v for v in x),file=f)
 print('LAST DEFINITIONS',file=f)
 for bit in[3957,1652,1650,1651,1653,1654]:
  hits=[]
  for i in range(5498330):
   x=struct.unpack_from('<7Q',final,i*56)
   if x[0]in(3,4,5,12)and x[4]==bit:hits.append((i,x))
  print(bit,[(i,tuple(-1 if v==none else v for v in x))for i,x in hits[-4:]],file=f)
