"""Freeze completed field-cause proof; exclude all separately active repair57 work."""
from pathlib import Path
import datetime,hashlib,json,subprocess
root=Path(__file__).resolve().parents[3];folder=Path(__file__).parent
lines=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','experiments/overnight-20261014/product'],cwd=root,text=True).splitlines()
files=[]
for line in lines:
 path=root/line[3:]
 if path.name in ['checkpoint-seventh-manifest.json','prepare-seventh-checkpoint-manifest.py']or path.name.startswith('repair57-'):continue
 if not path.is_file():continue
 raw=path.read_bytes();scope='exact_bytes'if path.suffix=='.patch'else'expected_git_blob_utf8_LF'
 if scope!='exact_bytes':raw=raw.decode('utf-8').replace('\r\n','\n').encode()
 files.append(dict(path=path.relative_to(root).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),hash_scope=scope))
doc=dict(prepared_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='completed_product_cause_and_finite_allMR_proofs_frozen',qualified_score=None,
 active_product_pids=[],excluded_active_prefixes=['repair57-'],scope='Completed actual fold producer and source-width borrow certificates, source-supported rail overflow certificate, finite fixed-prefix allfutureMR value/phase proofs; strict kernels unchanged. No repair or record claims. UTF8 LF predicts normalized Gitblob; patches exactbytes.',files=files)
(folder/'checkpoint-seventh-manifest.json').write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
print(len(files))
