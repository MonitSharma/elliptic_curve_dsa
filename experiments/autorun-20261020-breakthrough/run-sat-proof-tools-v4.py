import hashlib,json,os,resource,subprocess,tarfile,time,traceback
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;repos=r/'tool-repos';source=r.parent/'breakthrough-value-aig-audit-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def limit():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3));resource.setrlimit(resource.RLIMIT_FSIZE,(1024**3,1024**3))
def run(cmd,name,cwd=r,timeout=180,expected=(0,)):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,preexec_fn=limit);(r/(name+'.pid')).write_text(str(p.pid)+'\n');start=time.monotonic()
  try:code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:p.kill();code=p.wait();(r/(name+'-TIMEOUT.json')).write_text(json.dumps({'status':'INCONCLUSIVE_OWN_RECORDED_CHILD_WALL_TIMEOUT','seconds':timeout,'command':cmd})+'\n')
 (r/(name+'.exit')).write_text(str(code)+'\n');assert code in expected,(name,code);return code,time.monotonic()-start
try:
 import shutil
 previous=r.parent/'breakthrough-sat-proof-tools-20261020';assert(previous/'run.exit').read_text().strip()=='1';assert 'shadow' in(previous/'tests-kissat.log').read_text()
 original=json.loads((source/'SOLVER-DECLARATION.json').read_text());assert sha(source/'wrongpoint.cnf')==original['cnf_sha256'];oldfreeze=json.loads((previous/'SOURCE-FREEZE.json').read_text());freeze=oldfreeze['repositories'];assert all(sha(previous/'tool-repos'/name/p)==h for name,f in freeze.items()for p,h in f['files'].items());shutil.copytree(previous/'tool-repos',repos,symlinks=True)
 for name,f in freeze.items():shutil.copyfile(previous/(name+'-source.tar.gz'),r/(name+'-source.tar.gz'));assert sha(r/(name+'-source.tar.gz'))==f['source_archive_sha256']
 (r/'SOURCE-FREEZE.json').write_text(json.dumps({'repositories':freeze,'driver_sha256':sha(Path(__file__)),'previous_failed_driver_sha256':oldfreeze['driver_sha256'],'scope':'Exact previously frozen compiled tool/source copies. Original root-only permission test failure preserved. Full CLI signal-timing suite failed in previous release/debug builds and remains FAILED; qualify only SAT solving kernels/kitten under nobody-j2. Every proof claim independently checked by DRAT-trim; no source/OS permission edits.'},indent=2)+'\n')
 kissat=repos/'kissat';drat=repos/'drat-trim';run(['runuser','-u','nobody','--',str(kissat/'build/tissat'),'-j2','solve','kitten'],'tests-kissat-solving-kernels',kissat/'build',timeout=300);run(['make','-j2'],'build-drat',drat,timeout=180);solver=kissat/'build/kissat';checker=drat/'drat-trim';assert solver.is_file()and checker.is_file()
 (r/'BINARIES.json').write_text(json.dumps({'kissat_sha256':sha(solver),'drat_trim_sha256':sha(checker),'tool_source_freeze_sha256':sha(r/'SOURCE-FREEZE.json')},indent=2)+'\n')
 sat=r/'control-sat.cnf';sat.write_text('p cnf 1 1\n1 0\n');unsat=r/'control-unsat.cnf';unsat.write_text('p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n');run([str(solver),str(sat)],'control-sat',expected=(10,));run([str(solver),str(unsat),str(r/'control.drat')],'control-unsat',expected=(20,));run([str(checker),str(unsat),str(r/'control.drat')],'control-proof');assert's VERIFIED'in(r/'control-proof.log').read_text();invalid=r/'invalid.drat';invalid.write_text('0\n');code,_=run([str(checker),str(sat),str(invalid)],'control-invalid-proof',expected=(1,));assert's VERIFIED'not in(r/'control-invalid-proof.log').read_text()
 controls={'status':'SOLVING_KERNELS_AND_INDEPENDENT_PROOF_CONTROLS_PASS_FULL_CLI_SIGNAL_SUITE_REMAINS_FAILED','kissat_sha256':sha(solver),'drat_trim_sha256':sha(checker)};(r/'QUALIFICATION.json').write_text(json.dumps(controls,indent=2)+'\n');assert all(sha(repos/name/p)==h for name,f in freeze.items()for p,h in f['files'].items())
 (r/'FULL-CLI-SUITE-FAILURES.json').write_text(json.dumps({'status':'FAILED_SIGNAL_TIMING_NOT_RECAST_AS_PASS','logs':{n:sha(r.parent/n/'tests-kissat-unprivileged.log') if n.endswith('v2-20261020') else sha(r.parent/n/'tests-kissat-debug-unprivileged.log') for n in ['breakthrough-sat-proof-tools-v2-20261020','breakthrough-sat-proof-tools-v3-20261020']},'scope':'Full suite failure preserved. Solver is an untrusted proof producer; only independently checked DRAT proof can establish UNSAT.'},indent=2)+'\n');declaration={'at_utc':datetime.now(timezone.utc).isoformat(),'original_cnf_sha256':original['cnf_sha256'],'original_source_freeze_sha256':original['source_freeze_sha256'],'source_cnf':str(source/'wrongpoint.cnf'),'solver_sha256':sha(solver),'checker_sha256':sha(checker),'solver_wall_seconds':180,'checker_wall_seconds':180,'address_space_limit_GiB':6,'proof_file_limit_GiB':1,'scope':'Same first fixed source/input, independently qualified solver/proof checker. Not a gate, nonce search or quantum record.'};(r/'PROOF-DECLARATION.json').write_text(json.dumps(declaration,indent=2)+'\n')
 code,seconds=run([str(solver),str(source/'wrongpoint.cnf'),str(r/'wrongpoint.drat')],'solve',timeout=180,expected=(0,10,20,-9,-25));assert sha(source/'wrongpoint.cnf')==original['cnf_sha256'];result={'status':'INCONCLUSIVE_NO_VERIFIED_WRONGPOINT_PROOF','solver_exit':code,'solver_seconds':seconds,'cnf_sha256':original['cnf_sha256'],'nonce_screens':0,'proof_file_sha256':sha(r/'wrongpoint.drat')if(r/'wrongpoint.drat').exists()else None,'scope':declaration['scope']}
 if code==20:
  c,checked=run([str(checker),str(source/'wrongpoint.cnf'),str(r/'wrongpoint.drat')],'check-proof',timeout=180,expected=(0,1,-9,-25));result.update(checker_exit=c,checker_seconds=checked)
  if c==0 and's VERIFIED'in(r/'check-proof.log').read_text():result['status']='INDEPENDENTLY_CHECKED_WRONGPOINT_PROOF_FOR_ONE_FIXED_SOURCE_INPUT_NOT_A_NONCE_FILTER'
 elif code==10:result['status']='SAT_INCONCLUSIVE_FOR_WRONGPOINT_CERTIFICATE'
 (r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');traceback.print_exc();raise
