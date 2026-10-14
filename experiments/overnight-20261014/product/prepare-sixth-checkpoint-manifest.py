"""Freeze completed diagnostics with explicit expected Git-LF hash scope."""
from pathlib import Path
import datetime,hashlib,json,subprocess
root=Path(__file__).resolve().parents[3];folder=Path(__file__).parent
lines=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','experiments/overnight-20261014/product'],cwd=root,text=True).splitlines()
files=[]
for line in lines:
 path=root/line[3:]
 if path.name in ['checkpoint-sixth-manifest.json','prepare-sixth-checkpoint-manifest.py']:continue
 if not path.is_file():continue
 raw=path.read_bytes();scope='exact_bytes'if path.suffix=='.patch'else'expected_git_blob_utf8_LF'
 if scope!='exact_bytes':raw=raw.decode('utf-8').replace('\r\n','\n').encode()
 files.append(dict(path=path.relative_to(root).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),hash_scope=scope))
doc=dict(prepared_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='completed_product_artifacts_frozen',qualified_score=None,active_product_pids=[],
 scope='Completed three-source arithmetic comparison, body boundary failure+exact Y33 correction, full unchanged-stream observers, walk frames and independent exact tick-localization diagnostics. No repairs or qualified resource scores. UTF8 LF predicts normalized Git blob; patches exact bytes.',files=files)
(folder/'checkpoint-sixth-manifest.json').write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
print(len(files))
