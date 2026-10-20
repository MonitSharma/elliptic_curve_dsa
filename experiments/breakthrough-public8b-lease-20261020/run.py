"""Look for additional exact leases after the prior154 leases were installed."""
import hashlib,json,re,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';ws=r.parent;old=ws/'breakthrough-public54fc-lease-20261020/tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 assert not t.exists();t.mkdir()
 for name in ['Cargo.toml','Cargo.lock','discover.rs','io.rs']:shutil.copyfile(old/name,t/name)
 subprocess.run(['cp','-a','--reflink=auto',str(old/'target'),str(t/'target')],check=True)
 parent=ws/'breakthrough-public140-exact154-final-20261020/candidate/ops.bin';assert sha(parent)=='77d43b25b1526603b8e496da5f514a1b397a849bdd6eb9511e11beb0536e3057'
 dep=ws/'overnight-20261014/product-b3-baseline';protected=[dep/'Cargo.toml',dep/'Cargo.lock',dep/'src/circuit.rs',dep/'src/sim.rs',dep/'src/weierstrass_elliptic_curve.rs'];f={'tool_source_files':{p.relative_to(t).as_posix():sha(p)for p in t.iterdir()if p.is_file()},'protected_dependency_files':{str(p):sha(p)for p in protected},'input_sha256':sha(parent),'scope':'Unmodified arbitrary-cut guarded lease prover on complete751027 stream, after prior154 leases. Tests whether earlier fill/copy transformations expose further independent or multi-use leases. No new Q, packet content, gate or nonce. Parent official8b source equivalence must be independently verified before any final gate.'};(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','product_pareto_discover','--','--nocapture'],'tests');assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())==['4']
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','product_pareto_discover'],'build')
 assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
 run(['timeout','1800',str(t/'target/release/product_pareto_discover'),str(parent),str(r/'extra0')],'discover');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
