"""Record the exact set discrepancy from the preserved failed width control."""
from pathlib import Path
import re,ast,json,hashlib
root=Path(__file__).resolve().parent;p=root.parent/'carry-frame-20261015/evidence/cap1536-generation.log';text=p.read_text()
left=ast.literal_eval(re.search(r'left: (\[[^\]]*\])',text).group(1));right=ast.literal_eval(re.search(r'right: (\[[^\]]*\])',text).group(1))
out={'score':None,'parent_log_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actual_free_count':len(left),'expected_free_count':len(right),'actual_only':sorted(set(left)-set(right)),'expected_only':sorted(set(right)-set(left)),'actual_duplicates':len(left)-len(set(left)),'expected_duplicates':len(right)-len(set(right)),'scope':'Original failed free-set assertion only. New checkpoint validation must additionally prove fresh-ID bounds and unchanged live count.'}
assert out['expected_only']==[] and out['actual_duplicates']==out['expected_duplicates']==0
(root/'parent-failure.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
