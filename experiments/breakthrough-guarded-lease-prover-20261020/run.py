import hashlib,json,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args,log,cwd=t):
 with(r/log).open('xb')as out:p=subprocess.Popen(['timeout','1800']+args,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(log+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(log+'.exit')).write_text(str(rc)+'\n')
 if rc:(r/'run.exit').write_text(str(rc)+'\n');raise SystemExit(rc)
run(['python3','prepare.py'],'prepare.log',r);f=json.loads((r/'SOURCE_FREEZE.json').read_text());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','product_pareto_discover','--','--nocapture','--test-threads=1'],'tests.log');assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())==['4'];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','product_pareto_discover'],'build.log');binary=t/'target/release/product_pareto_discover';rows=[]
for name,meta in f['inputs'].items():
 path=Path(meta['path']);assert sha(path)==meta['sha256']and all(sha(t/p)==h for p,h in f['tool_source_files'].items())and all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());start=time.time();run([str(binary),str(path),str(r/name)],name+'.log');result=json.loads((r/(name+'.json')).read_text());row={'name':name,'seconds':time.time()-start,'input_sha256':sha(path),'binary_sha256':sha(binary),'proposed':result['proposed'],'proven_leases':len(result['leases']),'depth_weight_saving_diagnostic':result['depth_weight_saving_diagnostic'],'unproved':len(result['rejected_unproven']),'output_sha256':sha(r/(name+'.ops.bin')),'scope':'Exact scoped local proofs; native integration/full benchmark/gate pending.'};rows.append(row);(r/'DISCOVERY-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
(r/'DISCOVERY-RESULT.json').write_text(json.dumps({'status':'GUARDED_EXACT_DISCOVERY_COMPLETE_COMPONENT_ONLY','cases':rows},indent=2)+'\n');(r/'run.exit').write_text('0\n')
