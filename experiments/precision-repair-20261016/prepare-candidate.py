from pathlib import Path
import subprocess,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016')
family=json.loads((root/'PREDECLARED-FAMILY.json').read_text())
ranked=family['ranked_sites'];assert ranked,'No evidence-based eligible fold sites'
n=1;selection=ranked[:n];dest=root/'candidate-one-bit-top1';assert not dest.exists()
tip=root.parent/'product-exact-20261015/tip'
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(dest),family['source_revision']],check=True)
p=dest/'src/point_add/y15_onefold.rs';s=p.read_text()
old='''fn fold_window(t: usize, rev: bool) -> usize {
    if PAYLOAD_FOLD_PREFIX && !rev && t <= 99 { 57 } else { Y15_WIN }
}'''
assert s.count(old)==1
sel=', '.join(f'({str(e["reverse"]).lower()},{e["tick"]})'for e in selection)
new='''fn fold_window(t: usize, rev: bool) -> usize {
    let base = if PAYLOAD_FOLD_PREFIX && !rev && t <= 99 { 57 } else { Y15_WIN };
    // General precision increase selected from the independent fold-risk census.
    base + usize::from(['''+sel+'''].contains(&(rev,t)))
}'''
p.write_text(s.replace(old,new))
(root/'candidate-one-bit-top1.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'candidate-one-bit-top1-source.json').write_text(json.dumps(dict(base=family['source_revision'],selection=selection,source_hash=hashlib.sha256(p.read_bytes()).hexdigest(),family_sha256=hashlib.sha256((root/'PREDECLARED-FAMILY.json').read_bytes()).hexdigest(),optimization_assertions_unchanged=True),indent=2)+'\n')
print(json.dumps(selection))
