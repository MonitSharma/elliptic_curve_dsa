"""Fresh trusted evaluator checkout with no historical output files present."""
from pathlib import Path
import hashlib,json,subprocess,sys
base,dest,out=map(lambda s:Path(s).resolve(),sys.argv[1:4]);revision='c95b9325913abacca9c86bdebad10a20633cd04e'
git=lambda *args:subprocess.check_output(['git',*map(str,args)],text=True)
assert git('-C',base,'rev-parse','HEAD').strip()==revision
if not dest.exists():subprocess.check_call(['git','-C',str(base),'worktree','add','--detach',str(dest),revision])
assert git('-C',dest,'rev-parse','HEAD').strip()==revision
assert not git('-C',dest,'status','--porcelain').strip()
subprocess.check_call(['git','-C',str(dest),'sparse-checkout','set','--no-cone','/*','!/results.tsv','!/score.json'])
assert not dest.joinpath('results.tsv').exists()and not dest.joinpath('score.json').exists()
assert not git('-C',dest,'status','--porcelain').strip()
paths=git('-C',dest,'ls-tree','-r','--name-only','HEAD').splitlines()
protected=[p for p in paths if(p.startswith('src/')and not p.startswith('src/point_add/'))or p.startswith('Cargo.')or p.startswith('rust-toolchain')]
sha={}
for p in protected:
    data=(dest/p).read_bytes();old=subprocess.check_output(['git','-C',str(dest),'show',f'HEAD:{p}']);assert data==old,p;sha[p]=hashlib.sha256(data).hexdigest()
out.write_text(json.dumps(dict(scope='Unchanged protected evaluator source/Cargo/toolchain in isolated worktree; sparse exclusion only output files, no historical results edited',base_revision=revision,checkout=str(dest),historical_outputs_absent=True,protected_source_sha256=sha),indent=2)+'\n')
print(json.dumps(dict(base_revision=revision,checkout=str(dest),protected_files_verified=len(sha),historical_outputs_absent=True)))
