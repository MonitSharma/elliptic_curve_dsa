from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parent;e=root/'evidence';tree=root.parent/'product-exact-20261015/wide-candidate-final'
protected=json.loads((e/'protected.json').read_text())
for p,h in protected.items():assert hashlib.sha256((tree/p).read_bytes()).hexdigest()==h,p
changed=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines()
assert changed and all(p.startswith('src/point_add/') for p in changed),changed
score=json.loads((e/'score.json').read_text());print(json.dumps(score,indent=2))
(e/'final-candidate.patch').write_bytes(subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add']))
(e/'final-stream.sha256').write_text(hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()+'  ops.bin\n')
sources={str(p.relative_to(tree)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (tree/'src/point_add').rglob('*') if p.is_file()}
(e/'final-source.json').write_text(json.dumps(sources,indent=2)+'\n')
