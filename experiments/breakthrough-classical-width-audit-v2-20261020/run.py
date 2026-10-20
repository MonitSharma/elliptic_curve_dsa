import hashlib,json,subprocess,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'tool';old=ws/'breakthrough-stackv3-width-stats-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());t.mkdir();shutil.copyfile(old/'tool/io.rs',t/'io.rs');shutil.copyfile(r/'audit.rs',t/'audit.rs');shutil.copyfile(old/'tool/Cargo.lock',t/'Cargo.lock');s=(old/'tool/Cargo.toml').read_text();s=s[:s.index('[[bin]]')]+"[[bin]]\nname=\"classical_width_audit\"\npath=\"audit.rs\"\n[profile.release]\nopt-level=3\n";(t/'Cargo.toml').write_text(s);subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
 inputs={'public':ws/'breakthrough-stackv3-width-plan7-20261020/public/ops.bin','stronger28':ws/'breakthrough-stackv3-width-plan7-20261020/cap1234-t28/ops.bin'};expected={'public':'714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f','stronger28':'2bc0537813dcb2f8b0785c567ecdc5a8056b8c7afe8cffd4f78240c34d32de51'};assert all(sha(p)==expected[n]for n,p in inputs.items());freeze={'tool_source_files':{p:sha(t/p)for p in['audit.rs','io.rs','Cargo.toml','Cargo.lock']},'protected_dependency_files':f['protected_dependency_files'],'inputs':{n:{'path':str(p),'sha256':expected[n]}for n,p in inputs.items()},'scope':'Read-only classical taint/idle-slot nomination, no stream rewrite or scored result.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','classical_width_audit'],'tests');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','classical_width_audit'],'build')
 for n,p in inputs.items():run([str(t/'target/release/classical_width_audit'),str(p),str(r/(n+'.json'))],'audit-'+n)
 assert all(sha(t/p)==h for p,h in freeze['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in freeze['protected_dependency_files'].items());assert all(sha(p)==expected[n]for n,p in inputs.items());(r/'run.exit').write_text('0\n')
except Exception:
 (r/'run.exit').write_text('1\n');raise
