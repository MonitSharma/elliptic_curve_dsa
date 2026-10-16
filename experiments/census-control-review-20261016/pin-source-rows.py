from pathlib import Path
import json,hashlib,subprocess
r=Path('/home/hclau/ecdsa_research/census-control-review-20261016');b=r.parent;rev='4b2ec52fc55da796aa8f5ef851290297e8706424';tip=b/'product-exact-20261015/tip';N=2**64-1
data=subprocess.check_output(['git','-C',str(tip),'show',rev+':src/point_add/census_cut_data.txt']);assert data==(b/'census-control-family-20261016/inputs/census_cut_data.txt').read_bytes();(r/'census_cut_data.txt').write_bytes(data)
rows=[s.split()for s in data.decode().splitlines()if s.strip()and not s.lstrip().startswith('#')];rows.sort(key=lambda f:int(f[0]));all144=json.loads((r/'ALL144.json').read_text());assert len(rows)==len(all144)==144
for f,e in zip(rows,all144):
 old=[13 if f[1]=='ccx' else 14,int(f[2]),int(f[3]),int(f[4]),N,N if f[5]=='-' else int(f[5]),N];assert old==e['old']and int(f[0])==e['raw_index']and f[6]==e['action']
core=[dict(source_row_one_based=e['row']+1,legacy_index=e['legacy_index'],actual_index=e['actual_index'],old=e['old'],current=e['new'],source_anchor_sha3=e['anchor_sha3'])for e in all144 if e['new']is not None];assert len(core)==70
canonical=json.dumps(core,sort_keys=True,separators=(',',':')).encode();(r/'CORE70.json').write_text(json.dumps(core,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();out=dict(status='PASS ALL144 ROWS MATCH EXACT PUBLIC4B SOURCE',revision=rev,public_source_data_sha256=hashlib.sha256(data).hexdigest(),core70_canonical_sha256=hashlib.sha256(canonical).hexdigest(),review_sha256=sha(r/'REVIEW.json'),core_schema='JSON list in source row order, keys sorted, compact separators; excludes diagnostic-only fields',row_count=144,uniform_restore_family=70,deletions_retained=74)
(r/'SOURCE-ROW-PINS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
