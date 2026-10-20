import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;a=ws/'wide95-703-review-20261018-085419/candidate/src/point_add';b=ws/'breakthrough-primed-pool-20261020/observer/src/point_add';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();reports=[]
def constants(s):
 out={}
 for m in re.finditer(r'\bconst\s+([A-Za-z_0-9]+)\s*:[^=]+?=\s*(.*?);',s,re.S):
  value=' '.join(m[2].split());out[m[1]]=value if len(value)<500 else 'sha256:'+hashlib.sha256(value.encode()).hexdigest()
 return out
for p in sorted(a.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(a);q=b/rel
 if not q.is_file():continue
 ah,bh=sha(p),sha(q)
 if ah==bh:continue
 row={'path':rel.as_posix(),'bytes':[p.stat().st_size,q.stat().st_size],'sha256':[ah,bh]}
 if p.suffix=='.rs':
  ca,cb=constants(p.read_text().replace('\r','')),constants(q.read_text().replace('\r',''));row['constant_differences']={n:{'public_parent':ca.get(n),'spacious_lineage':cb.get(n)}for n in sorted(set(ca)|set(cb))if ca.get(n)!=cb.get(n)}
 reports.append(row)
result={'files':reports,'scope':'Complete common-file hash comparison and textual Rust constants including array types. Not a semantic proof or executed-profile trace. No source changes or gate verdict.'};(r/'ALL-SOURCE-COMPARISON.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
