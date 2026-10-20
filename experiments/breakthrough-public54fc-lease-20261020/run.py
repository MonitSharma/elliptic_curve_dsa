"""Re-run arbitrary-cut exact lease discovery on the current public product."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';ws=r.parent;old=ws/'breakthrough-guarded-lease-prover-20261020/tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 assert not t.exists();t.mkdir()
 for name in ['Cargo.toml','Cargo.lock','discover.rs','io.rs']:shutil.copyfile(old/name,t/name)
 subprocess.run(['cp','-a','--reflink=auto',str(old/'target'),str(t/'target')],check=True)
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','generate-lockfile','--offline'],'lock')
 parent=ws/'public-product-54fc-20261020/parent/ops.bin';assert sha(parent)=='51671a28145ce015d31b90db57c5bb248d544b0daacecfae1a015753056fa2e8'
 dep=ws/'overnight-20261014/product-b3-baseline';protected=[dep/'Cargo.toml',dep/'Cargo.lock',dep/'src/circuit.rs',dep/'src/sim.rs',dep/'src/weierstrass_elliptic_curve.rs'];f={'tool_source_files':{p.relative_to(t).as_posix():sha(p)for p in t.iterdir()if p.is_file()},'protected_dependency_files':{str(p):sha(p)for p in protected},'input_sha256':sha(parent),'scope':'Unmodified arbitrary-cut guarded lease prover applied to exact public54fc finished stream. Full-key proof on each accepted interval; fingerprints only nominate. Deterministic donors, no increased Q, final gate or nonce. Research diagnostic, not measured result.'};(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','product_pareto_discover','--','--nocapture'],'tests')
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','product_pareto_discover'],'build')
 assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
 run(['timeout','1800',str(t/'target/release/product_pareto_discover'),str(parent),str(r/'extra0')],'discover')
 (r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
