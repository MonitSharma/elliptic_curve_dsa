"""Freeze completed product artifacts using the root checkpoint's Git-LF scope."""
from pathlib import Path
import datetime, hashlib, json, subprocess
root=Path(__file__).resolve().parents[3]
folder=Path(__file__).parent
lines=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','experiments/overnight-20261014/product'],cwd=root,text=True).splitlines()
files=[]
for line in lines:
 path=root/line[3:]
 if path.name.startswith('checkpoint-fifth') or path.name=='prepare-fifth-checkpoint-manifest.py':continue
 if 'arithmetic-compare' in path.name:continue
 raw=path.read_bytes();scope='exact_bytes' if path.suffix=='.patch' else 'expected_git_blob_utf8_LF'
 if scope!='exact_bytes':
  try:raw=raw.decode('utf-8').replace('\r\n','\n').encode()
  except UnicodeDecodeError:
   if b'\0' in raw:scope='exact_binary_bytes'
   else:raw=raw.replace(b'\r\n',b'\n');scope='expected_git_blob_LF_original_text_encoding'
 files.append({'path':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'hash_scope':scope})
doc={'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'completed_product_artifacts_frozen','qualified_score':None,'active_product_pids':[],
 'scope':'Completed B3 diagnostics and H45 physical/actual-prefix proofs, failures retained; unbound metadataadapter absent. UTF8 LF hashes predict normalized Gitblob bytes; binary patches preserve exact bytes.',
 'files':files}
(folder/'checkpoint-fifth-manifest.json').write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
print(len(files))
