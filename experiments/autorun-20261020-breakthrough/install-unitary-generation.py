import hashlib,json,os,socket,subprocess,sys,tarfile
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research').resolve();assert socket.gethostname()=='LHC-104-070';bundle=Path(sys.argv[1]);receipt=json.loads(Path(sys.argv[2]).read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert sha(bundle)==receipt['archive_sha256'];allowed={'breakthrough-recycle-unitary-finished-20261021'}
with tarfile.open(bundle)as ar:
 assert {m.name for m in ar.getmembers()}==set(receipt['members'])
 for m in ar.getmembers():
  rel=Path(m.name);assert m.isfile()and not rel.is_absolute()and'..'not in rel.parts and rel.parts[0]in allowed and len(rel.parts)==2;folder=ws/rel.parts[0];assert not folder.is_symlink();p=ws/rel;assert p.resolve().is_relative_to(folder.resolve());data=ar.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==receipt['members'][m.name]
  if p.exists():assert p.is_file()and p.read_bytes()==data,str(p)
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
r=ws/'breakthrough-recycle-unitary-finished-20261021';pidfile=r/'pipeline.pid'
if pidfile.exists():print(json.dumps({'status':'ALREADY_LAUNCHED_DO_NOT_DUPLICATE','pid':int(pidfile.read_text()),'pipeline_exit':(r/'pipeline.exit').read_text().strip()if(r/'pipeline.exit').exists()else None,'archive_sha256':sha(bundle)}));raise SystemExit(0)
assert not(r/'candidate').exists()and not(ws/'breakthrough-recycle-unitary-final-gate-20261021/GATE-DECLARATION.json').exists();available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2;env=dict(os.environ,CARGO_BUILD_JOBS='4',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
with(r/'pipeline.log').open('xb')as log:p=subprocess.Popen(['nohup','python3','-u',str(r/'server-run.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
pidfile.write_text(str(p.pid)+'\n');out={'status':'LAUNCHED_NOHUP_NEW_SESSION','pid':p.pid,'hostname':socket.gethostname(),'archive_sha256':sha(bundle),'available_kib':available,'build_threads':4,'library_threads':1,'census_threads_total':16,'scope':'Generation/native17/officialbytecontrol ONLY; currentparent/freshgate separately. No nonce/benchmark/upload.'};(r/'LAUNCH-RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
