from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;src=root.parent/'dynamic-pool-20261015/wide-b3';dst=root/'window4-b3'
assert not dst.exists();rev=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(dst),rev],check=True)
for rel in subprocess.check_output(['git','-C',str(src),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():
 assert rel.startswith('src/point_add/');(dst/rel).parent.mkdir(parents=True,exist_ok=True);(dst/rel).write_bytes((src/rel).read_bytes())
p=dst/'src/point_add/y15_onefold.rs';s=p.read_text();assert s.count('const Y15_WIN: usize = 56;')==1;s=s.replace('const Y15_WIN: usize = 56;','const Y15_WIN: usize = 60;');assert s.count('{ 57 } else { Y15_WIN }')==1;s=s.replace('{ 57 } else { Y15_WIN }','{ 61 } else { Y15_WIN }');p.write_text(s)
(root/'window4-vs-parent.patch').write_bytes(subprocess.run(['diff','-ruN','-x','target','-x','ops.bin','-x','.git',str(src/'src'),str(dst/'src')],capture_output=True).stdout)
(root/'window4-full.patch').write_bytes(subprocess.check_output(['git','-C',str(dst),'diff','--binary']))
(root/'window4-manifest.json').write_text(json.dumps({'source':str(src),'base':rev,'hypothesis':'Uniform +4 actual Y15 payload fold bits in both directions, not FOLD_GUARD. Capacity experiment, not exact repair.','source_hashes':{str(p.relative_to(dst)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (dst/'src/point_add').rglob('*') if p.is_file()},'qualified_score':None},indent=2)+'\n')
