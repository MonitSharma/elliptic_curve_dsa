import hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'tool';candidate=ws/'breakthrough-public322-square-generic-20261020';old=ws/'breakthrough-public140-cache-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 while not(candidate/'run.exit').exists():time.sleep(2)
 assert(candidate/'run.exit').read_text().strip()=='0';cf=json.loads((candidate/'SOURCE-FREEZE.json').read_text());result=json.loads((candidate/'FINISHED-RESULT.json').read_text());assert all(sha(candidate/'candidate'/p)==h for p,h in{**cf['source_files'],**cf['protected_files']}.items());source=candidate/'candidate/ops.bin';assert sha(source)==result['native_stream_sha256']
 prior=json.loads((old/'SOURCE_FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in prior['tool_source_files'].items());assert not t.exists();t.mkdir()
 for name in['Cargo.toml','Cargo.lock','discover.rs','io.rs']:shutil.copyfile(old/'tool'/name,t/name)
 subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','generate-lockfile','--offline'],'lock')
 deps=prior['protected_dependency_files'];assert all(sha(Path(p))==h for p,h in deps.items());f={'tool_source_files':{p.relative_to(t).as_posix():sha(p)for p in t.iterdir()if p.is_file()},'protected_dependency_files':deps,'input':str(source),'input_sha256':sha(source),'candidate_source_freeze_sha256':sha(candidate/'SOURCE-FREEZE.json'),'candidate_result_sha256':sha(candidate/'FINISHED-RESULT.json'),'extra_donor_budget':16,'scope':'Unchanged bounded200000-op arbitrary-cut exact lease engine, independently qualified on fixed square1408 generic source. Full exact expressions accept proofs; fingerprints nominate only. Four native guarded/phase controls precede scan. Potential extra width is allowed for independent T objective. No final gate or nonce screening.'};(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','product_pareto_discover','--','--nocapture'],'tests');assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())==['4'];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','product_pareto_discover'],'build')
 assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());run(['timeout','1800',str(t/'target/release/product_pareto_discover'),str(source),str(r/'extra16')],'discover',env=dict(os.environ,RESEARCH_EXTRA_DONORS='16'));assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());(r/'run.exit').write_text('0\n');report=json.loads((r/'extra16.json').read_text());print(json.dumps({'leases':len(report['leases']),'diagnostic_saving':report['depth_weight_saving_diagnostic'],'source_qubits':result['qubits'],'max_donor':max((x[2]for x in report['leases']),default=None),'proposed':report['proposed'],'rejected':len(report['rejected_unproven'])}),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');raise
