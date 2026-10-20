import hashlib,json,os,resource,subprocess,tarfile,time,traceback
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;repos=r/'tool-repos';source=r.parent/'breakthrough-value-aig-audit-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def limit():
 resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3));resource.setrlimit(resource.RLIMIT_FSIZE,(1024**3,1024**3))
def run(cmd,name,cwd=r,timeout=180,expected=(0,)):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,preexec_fn=limit);(r/(name+'.pid')).write_text(str(p.pid)+'\n');start=time.monotonic()
  try:code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:p.kill();code=p.wait();(r/(name+'-TIMEOUT.json')).write_text(json.dumps({'status':'INCONCLUSIVE_OWN_RECORDED_CHILD_WALL_TIMEOUT','seconds':timeout,'command':cmd})+'\n')
 (r/(name+'.exit')).write_text(str(code)+'\n');assert code in expected,(name,code);return code,time.monotonic()-start
try:
 assert(source/'solver-controller.exit').read_text().strip()=='0';assert json.loads((source/'SOLVER-RESULT.json').read_text())['status']=='INCONCLUSIVE_SOLVER_EXCEPTION';original=json.loads((source/'SOLVER-DECLARATION.json').read_text());assert sha(source/'wrongpoint.cnf')==original['cnf_sha256'];repos.mkdir();freeze={}
 for name,url in [('kissat','https://github.com/arminbiere/kissat.git'),('drat-trim','https://github.com/marijnheule/drat-trim.git')]:
  t=repos/name;run(['git','clone','--depth','1',url,str(t)],'clone-'+name,timeout=180);revision=subprocess.check_output(['git','-C',str(t),'rev-parse','HEAD']).decode().strip();assert not subprocess.check_output(['git','-C',str(t),'status','--porcelain']).strip();files=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines();freeze[name]={'url':url,'revision':revision,'files':{p:sha(t/p)for p in files if(t/p).is_file()}}
  with tarfile.open(r/(name+'-source.tar.gz'),'w:gz')as archive:
   for p in sorted(freeze[name]['files']):archive.add(t/p,arcname=p,recursive=False)
  freeze[name]['source_archive_sha256']=sha(r/(name+'-source.tar.gz'))
 (r/'SOURCE-FREEZE.json').write_text(json.dumps({'repositories':freeze,'driver_sha256':sha(Path(__file__)),'scope':'Public SAT/proof tools only, frozen before compilation. No ECDSA source/harness change.'},indent=2)+'\n')
 kissat=repos/'kissat';drat=repos/'drat-trim';run(['./configure'],'configure',kissat);run(['make','-j2'],'build-kissat',kissat,timeout=300);run(['make','-j2','test'],'tests-kissat',kissat,timeout=300);run(['make','-j2'],'build-drat',drat,timeout=180);solver=kissat/'build/kissat';checker=drat/'drat-trim';assert solver.is_file()and checker.is_file()
 (r/'BINARIES.json').write_text(json.dumps({'kissat_sha256':sha(solver),'drat_trim_sha256':sha(checker),'tool_source_freeze_sha256':sha(r/'SOURCE-FREEZE.json')},indent=2)+'\n')
 sat=r/'control-sat.cnf';sat.write_text('p cnf 1 1\n1 0\n');unsat=r/'control-unsat.cnf';unsat.write_text('p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n');run([str(solver),str(sat)],'control-sat',expected=(10,));run([str(solver),str(unsat),str(r/'control.drat')],'control-unsat',expected=(20,));run([str(checker),str(unsat),str(r/'control.drat')],'control-proof');assert's VERIFIED'in(r/'control-proof.log').read_text();invalid=r/'invalid.drat';invalid.write_text('0\n');code,_=run([str(checker),str(sat),str(invalid)],'control-invalid-proof',expected=(1,));assert's VERIFIED'not in(r/'control-invalid-proof.log').read_text()
 controls={'status':'SOLVER_NATIVE_TESTS_SAT_UNSAT_AND_INDEPENDENT_VALID_INVALID_PROOF_CONTROLS_PASS','kissat_sha256':sha(solver),'drat_trim_sha256':sha(checker)};(r/'QUALIFICATION.json').write_text(json.dumps(controls,indent=2)+'\n');assert all(sha(repos/name/p)==h for name,f in freeze.items()for p,h in f['files'].items())
 declaration={'at_utc':datetime.now(timezone.utc).isoformat(),'original_cnf_sha256':original['cnf_sha256'],'original_source_freeze_sha256':original['source_freeze_sha256'],'source_cnf':str(source/'wrongpoint.cnf'),'solver_sha256':sha(solver),'checker_sha256':sha(checker),'solver_wall_seconds':180,'checker_wall_seconds':180,'address_space_limit_GiB':6,'proof_file_limit_GiB':1,'scope':'Same first fixed source/input, independently qualified solver/proof checker. Not a gate, nonce search or quantum record.'};(r/'PROOF-DECLARATION.json').write_text(json.dumps(declaration,indent=2)+'\n')
 code,seconds=run([str(solver),str(source/'wrongpoint.cnf'),str(r/'wrongpoint.drat')],'solve',timeout=180,expected=(0,10,20,-9,-25));assert sha(source/'wrongpoint.cnf')==original['cnf_sha256'];result={'status':'INCONCLUSIVE_NO_VERIFIED_WRONGPOINT_PROOF','solver_exit':code,'solver_seconds':seconds,'cnf_sha256':original['cnf_sha256'],'nonce_screens':0,'proof_file_sha256':sha(r/'wrongpoint.drat')if(r/'wrongpoint.drat').exists()else None,'scope':declaration['scope']}
 if code==20:
  c,checked=run([str(checker),str(source/'wrongpoint.cnf'),str(r/'wrongpoint.drat')],'check-proof',timeout=180,expected=(0,1,-9,-25));result.update(checker_exit=c,checker_seconds=checked)
  if c==0 and's VERIFIED'in(r/'check-proof.log').read_text():result['status']='INDEPENDENTLY_CHECKED_WRONGPOINT_PROOF_FOR_ONE_FIXED_SOURCE_INPUT_NOT_A_NONCE_FILTER'
 elif code==10:result['status']='SAT_INCONCLUSIVE_FOR_WRONGPOINT_CERTIFICATE'
 (r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');traceback.print_exc();raise
