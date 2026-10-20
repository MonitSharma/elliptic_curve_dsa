import collections,hashlib,json,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-public1829-width-port-local-v2-20261020';archive=root/'experiments/breakthrough-public1829-reproduction-20261020/point-add-source.tar.gz';out={}
with tarfile.open(archive)as a:
 for name in ['row_edits.txt','and_cache.txt','product_copy.txt','value_edits.txt']:
  raw=a.extractfile('src/point_add/'+name).read();lines=raw.decode().splitlines();removed=collections.Counter();added=collections.Counter()
  for line in lines[1:]:
   x=list(map(int,line.split()));n,z=x[1:3];assert len(x)==3+7*(n+z);removed.update(x[3:3+7*n:7]);added.update(x[3+7*n::7])
  out[name]={'sha256':hashlib.sha256(raw).hexdigest(),'rows':len(lines)-1,'removed_operation_kinds':dict(removed),'added_operation_kinds':dict(added),'static_ccx_ccz_delta':sum(added[k]-removed[k]for k in [13,14])}
result={'status':'PUBLIC_TABLE_STRUCTURE_DIAGNOSTIC_NOT_EXECUTED_RESOURCES','tables':out,'scope':'Raw operation-kind table differences only. Guarded execution and fresh proof context determine actual resource savings. Old source-bound tables never applied to changed constructors.'};(r/'PUBLIC-STATIC-TABLE-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(out))
