import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-context-lease-20261020';source=ws/'breakthrough-stackv3-width-20261020';t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items())and all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());assert(source/'run.exit').read_text().strip()=='0'and not t.exists();t.mkdir()
 for n in['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(old/'tool'/n,t/n)
 shutil.copyfile(r/'stats.rs',t/'stats.rs');p=t/'Cargo.toml';p.write_bytes(p.read_bytes()+b'\n[[bin]]\nname="native_width_stats"\npath="stats.rs"\n');subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True);inputs={row['mode']:source/row['mode']/'ops.bin'for row in json.loads((source/'RESULT.json').read_text())['cases']if row['exit']==0};freeze={'tool_source_files':{p.name:sha(p)for p in t.iterdir()if p.is_file()},'protected_dependency_files':f['protected_dependency_files'],'inputs':{n:{'path':str(p),'sha256':sha(p)}for n,p in inputs.items()},'scope':'Read-only protected analyze_ops and exact existing guard-depth diagnostic; no circuit change/gate/nonce/score.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','native_width_stats'],'build');rows={}
 for n,p in inputs.items():assert sha(p)==freeze['inputs'][n]['sha256'];run([str(t/'target/release/native_width_stats'),str(p),str(r/(n+'.json'))],'stats-'+n);rows[n]=json.loads((r/(n+'.json')).read_text())
 assert all(sha(t/p)==h for p,h in freeze['tool_source_files'].items());(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_STATIC_WIDTH_PROXY_DIAGNOSTICS','cases':rows},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
