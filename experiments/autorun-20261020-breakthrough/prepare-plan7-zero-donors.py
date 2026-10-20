from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-stackv3-plan7-zero-donors-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('tool/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n*.ops.bin\n')
(r/'PLAN.md').write_text('''# Exact context leases with zero added quantum wires

Fixed input: completed frozen1233/t28 generic-v2 output, before any development
inputs. Reuse the context16384 exact-proof engine, adding0 to the allowed donor
budget list and declaring0 explicitly. No proof algebra, lookback, same-scope,
clean/no-touch/nonoverlap or phase-repair rule changes. Existing7 native controls
already prove guarded cache rewrites using a donor within the original wire
range, including arbitrary classical data, phase faults and broken aliases.

Every accepted lease must reference only input quantum indices; measure the
rewritten complete stream with the protected analyzer and assert width never
increases. Fingerprints nominate only; full arbitrary-cut algebra must prove
every accepted rewrite. No gate/nonce/benchmark or scored result. Component
savings and the diagnostic guard-depth proxy are not executed fullcircuitT.
''')
(r/'run.py').write_text('''import hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;source=ws/'breakthrough-stackv3-plan7-generic-v2-20261020';old=ws/'breakthrough-context16384-lease-20261020';stats=ws/'breakthrough-stackv3-width-stats-20261020';t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 start=time.time()
 while not(source/'run.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());a=json.loads((source/'RESULT.json').read_text());assert a['qubits']==1233;assert all(sha(source/'candidate'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/'candidate/ops.bin';assert sha(input)==a['stream_sha256']
 of=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in of['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in of['protected_dependency_files'].items());t.mkdir()
 for p in of['tool_source_files']:shutil.copyfile(old/'tool'/p,t/p)
 p=t/'discover.rs';s=p.read_text();needle='assert!([16,64].contains(&extra));';assert s.count(needle)==1;s=s.replace(needle,'assert!([0,16,64].contains(&extra));');p.write_text(s);subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
 f={'tool_source_files':{p:sha(t/p)for p in of['tool_source_files']},'protected_dependency_files':of['protected_dependency_files'],'input':str(input),'input_sha256':sha(input),'input_source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'extra_donors':0,'lookback':16384,'scope':'Exact context component using only existing physical quantum wires; no scored result/gate/nonce.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\\n');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','product_pareto_discover','--','--nocapture'],'tests');assert re.findall(r'test result: ok\\. (\\d+) passed; 0 failed;',(r/'tests.log').read_text())==['7'];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','product_pareto_discover'],'build');start=time.time();run(['timeout','3600',str(t/'target/release/product_pareto_discover'),str(input),str(r/'zero-donors')],'discover',env=dict(os.environ,RESEARCH_EXTRA_DONORS='0'));proof=json.loads((r/'zero-donors.json').read_text());assert proof['peak_qubits']==1233 and all(x[2]<1233 for x in proof['leases']);assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());assert sha(input)==f['input_sha256']
 tf=json.loads((stats/'SOURCE-FREEZE.json').read_text());assert all(sha(stats/'tool'/p)==h for p,h in tf['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in tf['protected_dependency_files'].items());run([str(stats/'tool/target/release/native_width_stats'),str(r/'zero-donors.ops.bin'),str(r/'OUTPUT-STATS.json')],'stats',r);st=json.loads((r/'OUTPUT-STATS.json').read_text());assert st['qubits_protected_analyzer']<=1233
 result={'status':'ZERO_ADDED_WIRE_EXACT_CONTEXT_COMPONENT_NOT_SCORED','native_controls':7,'input_qubits':1233,'output_qubits':st['qubits_protected_analyzer'],'leases':len(proof['leases']),'proposed':proof['proposed'],'diagnostic_saving':proof['depth_weight_saving_diagnostic'],'output_stream_sha256':sha(r/'zero-donors.ops.bin'),'output_records_sha3':st['records_sha3'],'output_operations':st['operations'],'max_donor':max((x[2]for x in proof['leases']),default=None),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'seconds':time.time()-start};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\\n');(r/'run.exit').write_text('0\\n');print(json.dumps(result),flush=True)
except Exception:
 (r/'run.exit').write_text('1\\n');raise
''');print(r)
