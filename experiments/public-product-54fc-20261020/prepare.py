import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'parent';repo=ws/'toffoli';revision='3dee0cd67d09d40af62da06bc1c1c6b16adc8f56';base='90e777ea8242faa0acb2462c5cb5be7c318a2d64';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not t.exists();assert subprocess.check_output(['git','-C',str(repo),'rev-parse',revision]).decode().strip()==revision
changed=subprocess.check_output(['git','-C',str(repo),'diff','--name-only',base,revision]).decode().splitlines();assert all(p.startswith('src/point_add/')for p in changed)
subprocess.run(['git','-C',str(repo),'worktree','add','--detach',str(t),revision],check=True)
paths=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines();protected={p:sha(t/p)for p in paths if not p.startswith('src/point_add/')};assert len(protected)==17
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(ws/'classical12-final-20261020/candidate/target'),str(t/'target')],check=True)
with(r/'public-source.tar.gz').open('xb')as out:subprocess.run(['git','-C',str(repo),'archive','--format=tar.gz',revision],stdout=out,check=True)
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'revision':revision,'public_submission':'54fc4f25-b48c-4155-9c58-83d6f5d71de2','public_rounded_metrics':{'qubits':1234,'toffoli':761052,'product':939138168},'expected_native_stream_sha256':'51671a28145ce015d31b90db57c5bb248d544b0daacecfae1a015753056fa2e8','source_archive_sha256':sha(r/'public-source.tar.gz'),'protected_files':protected,'tracked_files':{p:sha(t/p)for p in paths},'scope':'Immutable fresh public parent reproduction. No source edits, candidate, census, nonce search or new record claim.'},indent=2)+'\n')
