from pathlib import Path
import subprocess,shutil,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');dest=root/'component-family16';base=root/'component-observer'
family=json.loads((root/'PREDECLARED-FAMILY.json').read_text());selection=family['ranked_sites'][:16]
subprocess.run(['git','-C',str(base),'worktree','add','--detach',str(dest),family['source_revision']],check=True)
shutil.copytree(base/'src/point_add',dest/'src/point_add',dirs_exist_ok=True)
p=dest/'src/point_add/y15_onefold.rs';s=p.read_text();a=s.index('fn fold_window(');b=s.index('\n}',a)+2
tuples=', '.join(f'({str(r["reverse"]).lower()},{r["tick"]})'for r in selection)
new='''fn fold_window(t: usize, rev: bool) -> usize {
    let base=if PAYLOAD_FOLD_PREFIX && !rev && t<=99 {57}else{Y15_WIN};
    base+usize::from(['''+tuples+'''].contains(&(rev,t)))
}''';p.write_text(s[:a]+new+s[b:])
p=dest/'src/point_add/fold_marks.rs';p.write_text(p.read_text().replace('precision-repair-20261016/component"','precision-repair-20261016/family16-component"'))
(root/'family16-component').mkdir(exist_ok=True)
(root/'family16-component-source.json').write_text(json.dumps(dict(selection=selection,component_only=True,files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
