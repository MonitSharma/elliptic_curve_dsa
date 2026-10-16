from pathlib import Path
import struct,json,hashlib,collections
r=Path(__file__).resolve().parent;p=r/'evidence/mr-mask-tip-v3.bin'
with p.open('rb')as f:
 h=f.read(32);assert h[:8]==b'MRMASK01';n,np,nr=struct.unpack('<QQQ',h[8:]);assert(np,nr)==(1024,512)
 f.seek(32+16*n);roots=struct.unpack('<512I',f.read(2048));rows=[]
 for j,root in enumerate(roots):
  f.seek(32+16*root);kind,a,b,aux=struct.unpack('<IIII',f.read(16));rows.append(dict(bit=j,root=root,kind=kind,a=a,b=b,aux=aux))
c=json.load(open(r/'evidence/mask-cones-v1.json'));counts=c['group_cones'][0]['all_group_counts']
for row in rows:row['cone_nodes']=counts[row['bit']]
non=[row for row in rows if row['kind'] not in [0,1]]
summary=dict(status='IMMUTABLE_MASK_ROOT_CLASSIFICATION',source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nodes=n,root_kinds=dict(collections.Counter(row['kind']for row in rows)),constant0_bits=[row['bit']for row in rows if row['kind']==0],constant1_bits=[row['bit']for row in rows if row['kind']==1],nonconstant_count=len(non),nonconstant_min_nodes=min(row['cone_nodes']for row in non),nonconstant_max_nodes=max(row['cone_nodes']for row in non),nonconstant_min_fraction=min(row['cone_nodes']for row in non)/n,all_roots=rows)
assert summary['source_sha256']=='560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d'
(r/'evidence/mask-cones-root-summary-v1.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k not in['all_roots','constant0_bits','constant1_bits']}))
