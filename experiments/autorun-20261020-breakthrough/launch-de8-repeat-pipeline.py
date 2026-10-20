import hashlib,json,os,socket,subprocess,tarfile
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');bundle=ws/'de8-repeat-final-pipeline.tar.gz';assert socket.gethostname()=='LHC-104-070';assert hashlib.file_digest(bundle.open('rb'),'sha256').hexdigest()=='16aa79ae5e043725209c2643a6baf3886873634c1400a3dc04c4c69a13e5273a'
allowed={'breakthrough-de8-repeat-finished-20261020','breakthrough-de8-repeat-finished-development-20261020','breakthrough-de8-repeat-final-gate-20261020','breakthrough-de8-repeat-nonce-20261020','breakthrough-de8-repeat-final-20261020'}
assert all(not(ws/n).exists()for n in allowed)
available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2
with tarfile.open(bundle)as ar:
 for m in ar.getmembers():
  p=Path(m.name);assert m.isfile()and not p.is_absolute()and'..'not in p.parts and p.parts[0]in allowed and len(p.parts)==2
  dest=ws/p;dest.parent.mkdir(exist_ok=True);assert not dest.exists();dest.write_bytes(ar.extractfile(m).read())
r=ws/'breakthrough-de8-repeat-finished-20261020';env=dict(os.environ,CARGO_BUILD_JOBS='4',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
with(r/'pipeline.log').open('xb')as log:
 p=subprocess.Popen(['nohup','python3',str(r/'run.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(r/'pipeline.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'directory':str(r),'build_threads':4,'max_census_threads':16,'memory_available_kib':available,'scope':'No upload before independent local evidence/current-record review. Final gate outcome final; no rerun/relabel/extension. Unrelated jobs untouched.'}))
