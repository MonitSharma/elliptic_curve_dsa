"""Bounded exact-CNF research solver; never a production nonce filter."""
import hashlib,json,subprocess,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-value-aig-audit-20261020';qual=root/'experiments/breakthrough-value-aig-cnf-qualification-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
if '--worker'in sys.argv:
 try:
  import z3
  z3.set_param('memory_max_size',2048);assert z3.get_param('memory_max_size')=='2048'
  controls=[]
  for name,text,expected in [('sat','p cnf 1 1\n1 0\n','sat'),('unsat','p cnf 1 2\n1 0\n-1 0\n','unsat'),('empty-clause','p cnf 0 1\n0\n','unsat')]:
   p=r/('solver-control-'+name+'.cnf');p.write_text(text);s=z3.Solver();s.set(timeout=1000);s.from_file(str(p));actual=str(s.check());assert actual==expected,(name,actual);controls.append({'name':name,'expected':expected,'actual':actual})
  s=z3.Solver();s.set(timeout=60000);start=time.monotonic();s.from_file(str(r/'wrongpoint.cnf'));parse=time.monotonic()-start;start=time.monotonic();verdict=s.check();result={'status':str(verdict).upper()+'_FIXED_SOURCE_INPUT_CNF','z3_version':z3.get_version_string(),'parse_seconds':parse,'solver_seconds':time.monotonic()-start,'memory_limit_MiB':2048,'solver_timeout_ms':60000,'controls':controls,'statistics':str(s.statistics()),'reason_unknown':s.reason_unknown()if verdict==z3.unknown else None,'scope':'One frozen source/input only; UNSAT is a wrongpoint proof under the qualified exact Boolean encoding, SAT/UNKNOWN inconclusive. No quantum resource result, no nonce screened/rejected, not a general failure model.'};(r/'SOLVER-WORKER-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 except BaseException as error:
  (r/'SOLVER-WORKER-RESULT.json').write_text(json.dumps({'status':'INCONCLUSIVE_SOLVER_EXCEPTION','error_type':type(error).__name__,'error':str(error),'scope':'No wrongpoint certificate or nonce rejection.'},indent=2)+'\n');traceback.print_exc();raise
 sys.exit(0)
assert(r/'run.exit').read_text().strip()=='0';assert(qual/'run.exit').read_text().strip()=='0';assert'test result: ok. 24 passed; 0 failed;'in(qual/'tests.log').read_text();f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());qf=json.loads((qual/'SOURCE-FREEZE.json').read_bytes());assert all(sha(r/'local-tool'/p)==h for p,h in f['source_files'].items());core=(r/'local-tool/aig.rs').read_bytes();assert hashlib.sha256(core).hexdigest()==qf['original_core_aig_sha256'];assert(qual/'local-tool/aig.rs').read_bytes().startswith(core)
assert not(r/'SOLVER-DECLARATION.json').exists();declaration={'at_utc':datetime.now(timezone.utc).isoformat(),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'cnf_sha256':sha(r/'wrongpoint.cnf'),'cnf_bytes':(r/'wrongpoint.cnf').stat().st_size,'qualifier_source_freeze_sha256':sha(qual/'SOURCE-FREEZE.json'),'solver_script_sha256':sha(Path(__file__)),'solver_wall_timeout_seconds':180,'solver_check_timeout_ms':60000,'memory_limit_MiB':2048,'scope':'First fixed input only; exact Boolean encoding controls24native/27fullsource comparisons precede solver. No challenge nonce selection, screen or rejection.'};(r/'SOLVER-DECLARATION.json').write_text(json.dumps(declaration,indent=2)+'\n')
try:
 with(r/'solver-worker.log').open('xb')as log:
  p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32'else 0);(r/'solver-worker.pid').write_text(str(p.pid)+'\n')
  try:code=p.wait(timeout=180)
  except subprocess.TimeoutExpired:p.kill();code=p.wait();(r/'SOLVER-WORKER-RESULT.json').write_text(json.dumps({'status':'INCONCLUSIVE_TOTAL_WALL_TIMEOUT','seconds':180,'scope':'Only own recorded solver child stopped; no certificate or nonce rejection.'},indent=2)+'\n')
 (r/'solver-worker.exit').write_text(str(code)+'\n');assert sha(r/'wrongpoint.cnf')==declaration['cnf_sha256'];result=json.loads((r/'SOLVER-WORKER-RESULT.json').read_bytes());(r/'SOLVER-RESULT.json').write_text(json.dumps({**result,'cnf_sha256':declaration['cnf_sha256'],'source_freeze_sha256':declaration['source_freeze_sha256'],'qualifier_native_controls':24,'nonce_screens':0},indent=2)+'\n');(r/'solver-controller.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:(r/'solver-controller.exit').write_text('1\n');raise
