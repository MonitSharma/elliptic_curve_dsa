from pathlib import Path
import hashlib,json,tarfile
from datetime import datetime,timezone
a=Path(__file__).parent;root=a.parents[1];ex=root/'experiments';old=ex/'breakthrough-output-audit-20261020';r=ex/'breakthrough-public1829-local-development-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();f=json.loads((old/'TOOL-SOURCE-FREEZE-v2.json').read_bytes())
with tarfile.open(old/'native-source-and-tests.tar.gz')as archive:
 for rel,h in f['source_files'].items():
  data=archive.extractfile('tool-v2/'+rel).read();assert sha(data)==h,rel;p=t/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
p=t/'Cargo.toml';text=p.read_text().replace('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline','../../breakthrough-value-guard-fusion-audit-20261020/local-protected');assert '/home/hclau/'not in text;p.write_text(text)
src=ex/'breakthrough-public1829-width-port-local-v4-20261020';context=ex/'breakthrough-public1829-context-audit-20261020';assert(context/'run.exit').read_text().strip()=='0';cf=json.loads((context/'SOURCE-FREEZE.json').read_bytes());sf=json.loads((src/'SOURCE-FREEZE.json').read_bytes());assert all(sha((src/'observer'/p).read_bytes())==h for p,h in {**sf['source_files'],**sf['protected_files']}.items())
paths={'public1829':src/'public/ops.bin','cap1234':context/'cap1234-t21.ops.bin','cap1233':context/'cap1233-r012.ops.bin'};plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'public1829-workspace-cache-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':2,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p.read_bytes())for n,p in paths.items()},'scope':'Fresh full-output actual-resource DEVELOPMENT only on all3 fixed newpublic/cache streams. Native9constructor and9freshcontext proof controls passed before inputs. Public16567 exact, protected17 unchanged. Preserve every mismatch/value/phase/dirty outcome. No finished source, finalgate, nonce or quantum record.'};assert plan['streams']['public1829']=='16567ee18910b8ee9f7aca60c33f0aa88df9679e6528fa5a7884e74e1a877baf';(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
(r/'SOURCE-FREEZE.json').write_text(json.dumps({'tool_source_files':{rel:sha((t/rel).read_bytes())for rel in f['source_files']},'protected_files':sf['protected_files'],'original_observer_source_freeze_sha256':sha((old/'TOOL-SOURCE-FREEZE-v2.json').read_bytes()),'constructor_source_freeze_sha256':sha((src/'SOURCE-FREEZE.json').read_bytes()),'fresh_context_source_freeze_sha256':sha((context/'SOURCE-FREEZE.json').read_bytes()),'plan_sha256':sha((r/'PLAN.json').read_bytes()),'scope':plan['scope']},indent=2)+'\n')
s=(ex/'breakthrough-exact-witness-development-20261020/diagnostic.py').read_text();start=s.index("candidate=ws/'");end=s.index(';records={}',start)
s=s[:start]+'''candidate=ws/'breakthrough-public1829-width-port-local-v4-20261020';cf=json.loads((candidate/'SOURCE-FREEZE.json').read_text());tf=json.loads((r/'SOURCE-FREEZE.json').read_text());exe=r/'local-tool/target/release/product_paired_diagnostic'
assert all(sha(r/'local-tool'/p)==h for p,h in tf['tool_source_files'].items());deps=ws/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in tf['protected_files'].items());assert all(sha(candidate/'observer'/p)==h for p,h in {**cf['source_files'],**cf['protected_files']}.items());paths={name:Path(f['paths'][name])for name in f['streams']};assert all(sha(paths[n])==h for n,h in f['streams'].items());(r/'REPLAY-FREEZE.json').write_text(json.dumps({'plan_sha256':sha(r/'PLAN.json'),'tool_source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'binary_sha256':sha(exe),'streams':{n:{'path':str(p),'sha256':sha(p)}for n,p in paths.items()},'scope':f['scope']},indent=2)+'\\n')'''+s[end:]
s=s.replace("records['public2bd']","records['public1829']").replace("name=='public2bd'","name=='public1829'")
# Paths written on Windows must be rebased without changing the frozen plan.
needle="paths={name:Path(f['paths'][name])for name in f['streams']}";s=s.replace(needle,"paths={'public1829':candidate/'public/ops.bin','cap1234':ws/'breakthrough-public1829-context-audit-20261020/cap1234-t21.ops.bin','cap1233':ws/'breakthrough-public1829-context-audit-20261020/cap1233-r012.ops.bin'}")
(r/'diagnostic.py').write_text(s);(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.jsonl\n');(r/'.gitattributes').write_text('* -text\n')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-public1829-local-development-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export RAYON_NUM_THREADS=1
ulimit -v 8388608
trap 's=$?; printf "%s\\n" "$s" > controller.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path local-tool/Cargo.toml > build.log 2>&1
python3 diagnostic.py
'''.replace('BASE',base)).encode());(r/'launch-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-public1829-local-development-20261020
test ! -e controller.pid
nohup setsid sh run-local.sh > controller.log 2>&1 < /dev/null &
printf '%s\\n' "$!" > controller.pid
cat controller.pid
'''.replace('BASE',base)).encode());(r/'PLAN.md').write_text('''# Actual resource development of the new public workspace candidates

Fresh declared label public1829-workspace-cache-development-20261020-v1,
512x64shots/source,2workers,8fullprotected scalar batches for each stream. Compare
exact public1829 with BOTH fresh proven cached Q1234 andQ1233 prototypes. Preserve
all output/phase/dirty mismatches; no failurebased case selection. Source and
proof controls9+9 passed, all fullstream/source hashes frozen before inputs.
Observer source restores exact archived full-output v2 bytes except localCargo
dependency path, same17protected files exact. This is development, not a final
gate or score. No nonce search or upload; a competitive case needs literal
finished construction/full bindings/finalgate/unchangedbenchmark first.
''');print(r.name)
