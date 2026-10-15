from pathlib import Path
import shutil,subprocess,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');dest=root/'component-observer';base=root/'observer-tip'
assert (root/'candidate.exit').read_text().strip()=='101'
subprocess.run(['git','-C',str(base),'worktree','add','--detach',str(dest),'4b2ec52fc55da796aa8f5ef851290297e8706424'],check=True)
shutil.copytree(base/'src/point_add',dest/'src/point_add',dirs_exist_ok=True)
p=dest/'src/point_add/y15_onefold.rs';s=p.read_text();candidate=(root/'candidate-one-bit-top1/src/point_add/y15_onefold.rs').read_text()
def region(s):
 a=s.index('fn fold_window(');b=s.index('\n}',a)+2;return a,b,s[a:b]
a,b,old=region(s);_,_,new=region(candidate);p.write_text(s[:a]+new+s[b:])
p=dest/'src/point_add/fold_marks.rs';s=p.read_text().replace('let root="/home/hclau/ecdsa_research/precision-repair-20261016"','let root="/home/hclau/ecdsa_research/precision-repair-20261016/component"')
assert s.count('raw_ops={} score=NONE')==1
s=s.replace('ops.len());}','ops.len());eprintln!("COMPONENT_ONLY exit before optimization tables; no full circuit or score emitted");std::process::exit(0);}')
p.write_text(s);(root/'component').mkdir(exist_ok=True)
(root/'component-observer.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'component-source.json').write_text(json.dumps(dict(component_only=True,base='4b2ec52fc55da796aa8f5ef851290297e8706424',files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
print('Prepared raw component observer; never a complete candidate')
