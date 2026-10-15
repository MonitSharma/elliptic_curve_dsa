from pathlib import Path
import subprocess,shutil,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-family-20261016');old=root.parent/'precision-repair-20261016';base=old/'component-observer';dest=root/'component-late-forward'
family=json.loads((root/'PREDECLARED-FAMILY.json').read_text())
assert subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],text=True).strip()==family['source_revision']
(root/'base-status.txt').write_bytes(subprocess.check_output(['git','-C',str(base),'status','--short']))
subprocess.run(['git','-C',str(base),'worktree','add','--detach',str(dest),family['source_revision']],check=True)
shutil.copytree(base/'src/point_add',dest/'src/point_add',dirs_exist_ok=True)
p=dest/'src/point_add/y15_onefold.rs';s=p.read_text();a=s.index('fn fold_window(');b=s.index('\n}',a)+2
new='''fn fold_window(t: usize, rev: bool) -> usize {
    let base=if PAYLOAD_FOLD_PREFIX && !rev && t<=99 {57}else{Y15_WIN};
    base+usize::from(!rev && t>=100)
}''';p.write_text(s[:a]+new+s[b:])
p=dest/'src/point_add/fold_marks.rs';s=p.read_text();assert s.count('precision-repair-20261016/component"')==1;s=s.replace('precision-repair-20261016/component"','precision-family-20261016/component"');p.write_text(s);(root/'component').mkdir()
(root/'component-source.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'component-source.json').write_text(json.dumps(dict(family=family,component_only=True,files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
