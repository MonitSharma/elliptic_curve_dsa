from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-de8-generic-development-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir()
old=ex/'breakthrough-public1829-local-development-v2-20261020';f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for n,h in f['tool_source_files'].items():
 assert sha(old/'local-tool'/n)==h;p=t/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'local-tool'/n,p)
shutil.copyfile(old/'tests.log',r/'original-qualified-tests.log')
assert 'avx2_all_operations_captured_guards_rng_and_toffoli_match_full_protected_simulator ... ok'in(r/'original-qualified-tests.log').read_text()
f.update(scope='Fresh actual-resource development of fixed206file second-cache/generic source against exact officialde8. UNCHANGED previously qualified AVX2 observer source and existing binary; native qualification retained,8full protected scalar state/RNG/T batches repeated per source.512x64 per source, no finalgate/nonce/benchmark/score.',prior_tool_freeze_sha256=sha(old/'SOURCE-FREEZE.json'),original_native_qualification_sha256=sha(r/'original-qualified-tests.log'))
paths={'official_de8':ex/'breakthrough-local-de8-replay-20261020/candidate/ops.bin','generic':ex/'breakthrough-de8-generic-repeat-v3-20261020/candidate/ops.bin'}
plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'de8-two-cache-generic-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':2,'protected_scalar_batches':8,'streams':{n:sha(p)for n,p in paths.items()},'scope':f['scope']}
(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
s=(old/'diagnostic.py').read_text().replace("candidate=ws/'breakthrough-public1829-width-port-local-v4-20261020'","candidate=ws/'breakthrough-de8-generic-repeat-v3-20261020'").replace("candidate/'observer'/p","candidate/'candidate'/p").replace("exe=r/'local-tool/target/release/product_paired_diagnostic'","exe=ws/'breakthrough-public1829-local-development-v2-20261020/local-tool/target/release/product_paired_diagnostic'")
start=s.index("paths={'public1829':");end=s.index(';assert all(sha(paths[n])',start)
s=s[:start]+"paths={'official_de8':ws/'breakthrough-local-de8-replay-20261020/candidate/ops.bin','generic':candidate/'candidate/ops.bin'}"+s[end:]
s=s.replace("records['public1829']","records['official_de8']").replace("if name=='public1829':","if name=='official_de8':")
(r/'diagnostic.py').write_text(s)
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-de8-generic-development-20261020
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export RAYON_NUM_THREADS=1
ulimit -v 8388608
trap 's=$?; printf "%s\\n" "$s" > controller.exit' EXIT
python3 diagnostic.py
'''.replace('BASE',base)).encode())
(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.jsonl\n');(r/'.gitattributes').write_text('* -text\n')
(r/'PLAN.md').write_text('''# Actual paired development before selecting a final source

Fixed source206/17 protected bytes generated before inputs. Compare unchanged
officialde8 with second2cache+repeatedgeneric source on fresh predeclared512x64
inputs,2workers,8full protected complete-state/RNG/Toffoli scalar batches each.
Use BYTE-UNCHANGED previously qualified AVX2 observer and retain native control
evidence; no redundant tool rebuild. Preserve every target/other-register,
value/phase/dirty mismatch. Static estimate8T must be checked by executed means.
Development only, no new finalgate, nonce search, benchmark or record claim.
''');print(r.name)
