import hashlib,json,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;source=ws/'breakthrough-stackv3-width-plan7-20261020';tool=ws/'breakthrough-stackv3-width-stats-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 while not(source/'run.exit').exists():time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0'and(tool/'run.exit').read_text().strip()=='0';f=json.loads((tool/'SOURCE-FREEZE.json').read_text());sf=json.loads((source/'SOURCE-FREEZE.json').read_text());assert all(sha(tool/'tool'/p)==h for p,h in f['tool_source_files'].items())and all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());assert all(sha(source/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());rows=json.loads((source/'RESULT.json').read_text())['cases'];inputs={x['mode']:{'path':str(source/x['mode']/'ops.bin'),'sha256':x['stream_sha256']}for x in rows if x['exit']==0};exe=tool/'tool/target/release/native_width_stats';(r/'INPUT-DECLARATION.json').write_text(json.dumps({'source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'tool_source_freeze_sha256':sha(tool/'SOURCE-FREEZE.json'),'tool_binary_sha256':sha(exe),'inputs':inputs,'scope':'Read-only protected analyzer plus diagnostic guard-depth proxy. Nominal budget is not measuredQ. No benchmark/nonce/gate or scored result.'},indent=2)+'\n');results={}
 for n,x in inputs.items():
  path=Path(x['path']);assert sha(path)==x['sha256']
  with(r/('stats-'+n+'.log')).open('xb')as out:p=subprocess.Popen([str(exe),str(path),str(r/(n+'.json'))],stdout=out,stderr=subprocess.STDOUT);(r/('stats-'+n+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
  (r/('stats-'+n+'.exit')).write_text(str(rc)+'\n');assert rc==0;assert sha(path)==x['sha256'];results[n]=json.loads((r/(n+'.json')).read_text());print(json.dumps({'case':n,**results[n]}),flush=True)
 (r/'RESULT.json').write_text(json.dumps({'status':'PLAN7_STATIC_RESOURCE_DIAGNOSTIC_ONLY','cases':results},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
