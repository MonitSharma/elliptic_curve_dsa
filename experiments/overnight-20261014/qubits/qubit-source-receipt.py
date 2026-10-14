"""Record source and patch hashes for an isolated research checkout."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

checkout, patch, output = map(lambda s:Path(s).resolve(),sys.argv[1:4])
scope = sys.argv[4]
changed=subprocess.check_output(['git','-C',str(checkout),'diff','--name-only'],text=True).splitlines()
assert all(p.startswith('src/point_add/') for p in changed),changed
files=['src/point_add/frogdrop.rs','src/point_add/midg.rs','src/point_add/tests_midg_k24.rs']
body=dict(scope=scope,base_revision=subprocess.check_output(['git','-C',str(checkout),'rev-parse','HEAD'],text=True).strip(),
          checkout=str(checkout),candidate_changed_paths=changed,protected_files_modified=False,
          patch_sha256=hashlib.sha256(patch.read_bytes()).hexdigest(),
          source_sha256={p:hashlib.sha256(checkout.joinpath(p).read_bytes()).hexdigest() for p in files})
output.write_text(json.dumps(body,indent=2)+'\n');print(json.dumps(body,indent=2))
