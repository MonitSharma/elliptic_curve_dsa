from pathlib import Path
import hashlib,json,os,subprocess,tarfile
ws=Path('/home/hclau/ecdsa_research');bundle=ws/'de8-repeat-proof-package.tar.gz';assert hashlib.file_digest(bundle.open('rb'),'sha256').hexdigest()=='7b5eb6ac1fc6e73746d2ea42c6d5e54c59de20076f0b2647daf000f5cc74f875'
new={'breakthrough-de8-second-cache-20261020','breakthrough-de8-generic-repeat-v3-20261020','breakthrough-de8-generic-development-20261020'};final='breakthrough-de8-repeat-final-20261020';assert all(not(ws/n).exists()for n in new)
with tarfile.open(bundle)as ar:
 members=ar.getmembers()
 for m in members:
  p=Path(m.name);assert m.isfile()and not p.is_absolute()and'..'not in p.parts and len(p.parts)==2 and p.parts[0]in new|{final};assert not(ws/p).exists()
 for m in members:
  p=ws/m.name;p.parent.mkdir(exist_ok=True);p.write_bytes(ar.extractfile(m).read())
r=ws/final;assert not(r/'review.pid').exists();env=dict(os.environ,CARGO_BUILD_JOBS='4',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
with(r/'review.log').open('xb')as log:p=subprocess.Popen(['nohup','python3',str(r/'review.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(r/'review.pid').write_text(str(p.pid)+'\n');print(json.dumps({'review_pid':p.pid,'scope':'Wait for unchangedbenchmark/pipeline completion, then verify and seal source/evidence. No upload before local verification receipt and freshcurrentrecord check.'}))
