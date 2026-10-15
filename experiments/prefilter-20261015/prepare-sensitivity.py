from pathlib import Path
import csv,json
r=Path(__file__).parent
bad={}
for line in Path('/home/hclau/ecdsa_research/product-tip-20261015/tip-census.jsonl').read_text().splitlines():
 x=json.loads(line)
 for f in x['failures']:bad[(x['batch'],f['lane'])]=f
rows=[]
with (r/'evidence/census-coordinates4096.tsv').open()as f:
 for x in csv.DictReader(f,delimiter='\t'):
  key=(int(x['batch']),int(x['lane']))
  if key in bad:rows.append((x,bad[key]))
assert len(rows)==len(bad)
packet=r/'packets/all-failing-tip.tsv'
packet.write_text(''.join(str(i)+' '+' '.join(x[k]for k in ['tx','ty','ox','oy','ex','ey'])+'\n'for i,(x,_)in enumerate(rows)))
(r/'packets/all-failing-tip.metadata.json').write_text(json.dumps([dict(f,batch=x['batch'],lane=x['lane'])for x,f in rows],indent=2)+'\n')
structured=[];seen=set()
for path in ['/home/hclau/ecdsa_research/product-exact-20261015/flags-four-20261016/product-structured.tsv','/home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/structured.tsv','/home/hclau/ecdsa_research/product-focus-20261015/cache-replay-v2/structured.tsv']:
 for row in Path(path).read_text().splitlines():
  coords=tuple(row.split()[1:])
  if coords not in seen:seen.add(coords);structured.append(coords)
(r/'packets/sensitivity-structured.tsv').write_text(''.join(str(i)+' '+' '.join(x)+'\n'for i,x in enumerate(structured)))
print(json.dumps(dict(failing_shots=len(rows),value_shots=sum(x['value']for _,x in rows),phase_shots=sum(x['phase']for _,x in rows),dirty_shots=sum(x['dirty']for _,x in rows),structured_unique=len(structured))))
