"""Isolate the passing Q692 source and replace only its unclipped V increments."""
from pathlib import Path
import hashlib, json, subprocess, sys

frozen, patch, root = map(Path, sys.argv[1:4])
root.mkdir(parents=True, exist_ok=True)
candidate = root / 'candidate-control-fold-v1'
assert not candidate.exists()
subprocess.run(['git', 'clone', '--shared', '--no-hardlinks', str(frozen), str(candidate)], check=True)
subprocess.run(['git', '-C', str(candidate), 'apply', str(patch)], check=True)
assert subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD'],text=True).strip() == 'c95b9325913abacca9c86bdebad10a20633cd04e'
p = candidate / 'src/point_add/midg.rs'
s = p.read_text(encoding='utf8')
old = 'let predicate=rec(b,|b|for selector in &selectors{mc_xor(b,selector,g0,&[],&s.dirty);});'
new = '''// SX0 enters zero after the odd-divisor restoring step. Fold the
            // complete enable condition into it, then use a single-control
            // exact dirty increment. ACT, r0 and SY are unchanged by that
            // increment, so replaying the predicate restores SX0 exactly.
            let predicate=rec(b,|b|for selector in &selectors{
                let mut controls=vec![(act,false),(r[0],false)];
                controls.extend(selector.iter().copied());
                mc_xor(b,&controls,g0,&[],&s.dirty);
            });'''
assert s.count(old) == 2
s = s.replace(old, new)
old = 'inc_with_controls(b,&bits,&[(act,false),(r[0],false),(g0,false)],&s.dirty);'
assert s.count(old) == 2
s = s.replace(old, 'inc_mixed(b,g0,&bits,&s.anc,&s.dirty);')
p.write_text(s, encoding='utf8', newline='\n')
full_patch = subprocess.check_output(['git','-C',str(candidate),'diff','HEAD','--','src/point_add/'])
(root/'candidate-control-fold-v1.patch').write_bytes(full_patch)
delta = subprocess.check_output(['git','diff','--no-index','--',str(frozen/'src/point_add/midg.rs'),str(p)], stderr=subprocess.DEVNULL) if False else None
changed = subprocess.check_output(['git','-C',str(candidate),'diff','HEAD','--name-only'],text=True).splitlines()
assert all(x.startswith('src/point_add/') for x in changed)
manifest = dict(candidate=str(candidate), frozen_source=str(frozen), base_revision='c95b9325913abacca9c86bdebad10a20633cd04e', scope='unclipped V predicate fold only; no arithmetic-domain changes', changed_paths=changed, patch_sha256=hashlib.sha256(full_patch).hexdigest(), source_sha256={p.relative_to(candidate).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((candidate/'src/point_add').rglob('*')) if p.is_file()})
(root/'candidate-control-fold-v1-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
