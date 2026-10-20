import hashlib,json,os,resource,subprocess,time,traceback
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-sat-proof-tools-v5-20261020';aig=r.parent/'breakthrough-value-aig-audit-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();fds=[]
def limits():resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
try:
 assert(old/'run.exit').read_text().strip()=='0';previous=json.loads((old/'RESULT.json').read_text());assert previous['solver_exit']==20 and previous['checker_exit']==-9;decl=json.loads((old/'PROOF-DECLARATION.json').read_text());checker=old/'tool-repos/drat-trim/drat-trim';cnf=aig/'wrongpoint.cnf';proof=old/'wrongpoint.drat';assert sha(checker)==decl['checker_sha256'];assert sha(cnf)==previous['cnf_sha256'];assert sha(proof)==previous['proof_file_sha256'];mem=dict((l.split(':')[0],int(l.split()[1])*1024)for l in Path('/proc/meminfo').read_text().splitlines()if ':'in l and len(l.split())>=2 and l.split()[1].isdigit());assert mem['MemAvailable']>=8*1024**3
 plan={'at_utc':datetime.now(timezone.utc).isoformat(),'cnf_sha256':previous['cnf_sha256'],'proof_sha256':previous['proof_file_sha256'],'checker_sha256':decl['checker_sha256'],'previous_check_status':'INCONCLUSIVE_180_SECONDS','checker_seconds':900,'address_space_limit_GiB':6,'available_memory_bytes_before_launch':mem['MemAvailable'],'driver_sha256':sha(Path(__file__)),'scope':'Same exact proof and source/input. RAM transport and longer CHECK budget only; no solver/circuit/gate/nonce change.'};(r/'CHECK-DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
 for name,path,expected in [('cnf',cnf,previous['cnf_sha256']),('proof',proof,previous['proof_file_sha256'])]:
  fd=os.memfd_create('ecdsa-'+name,0);fds.append(fd);h=hashlib.sha256()
  with path.open('rb')as data:
   while chunk:=data.read(1024*1024):
    h.update(chunk)
    at=0
    view=memoryview(chunk)
    while at<len(view):
     at+=os.write(fd,view[at:])
  assert h.hexdigest()==expected;os.lseek(fd,0,os.SEEK_SET)
 started=time.monotonic()
 with(r/'check.log').open('xb')as log:
  cmd=['stdbuf','-oL','-eL',str(checker),f'/proc/self/fd/{fds[0]}',f'/proc/self/fd/{fds[1]}','-t','900'];p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(fds),preexec_fn=limits);(r/'check.pid').write_text(str(p.pid)+'\n')
  try:code=p.wait(timeout=930)
  except subprocess.TimeoutExpired:p.kill();code=p.wait()
 elapsed=time.monotonic()-started;(r/'check.exit').write_text(str(code)+'\n');verified=code==0 and's VERIFIED'in(r/'check.log').read_text();result={'status':'INDEPENDENTLY_CHECKED_WRONGPOINT_PROOF_FOR_ONE_FIXED_SOURCE_INPUT_NOT_A_NONCE_FILTER'if verified else'INCONCLUSIVE_NO_CHECKED_WRONGPOINT_PROOF','checker_exit':code,'checker_seconds':elapsed,'cnf_sha256':plan['cnf_sha256'],'proof_sha256':plan['proof_sha256'],'checker_sha256':plan['checker_sha256'],'nonce_screens':0,'scope':plan['scope']};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:(r/'run.exit').write_text('1\n');traceback.print_exc();raise
finally:
 for fd in fds:os.close(fd)
