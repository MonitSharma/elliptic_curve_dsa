"""Finalize unfrozen N274 fixtures and freeze the component-only source."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(sys.argv[1]); source=root/'candidate-n274-v1'; evidence=root/'evidence'
p=source/'src/point_add/tests_frogdrop.rs';t=p.read_text();a=t.index('fn n274_maps_counter_and_switch_lifetimes_native()');head,tail=t[:a],t[a:]
assert 'put(&mut input, &q[..121], lane, &x);' in tail
tail=tail.replace('put(&mut input, &q[..121], lane, &x);','put(&mut input, if cp.dn{&q[..121]}else{&q}, lane, &x);')
tail=tail.replace('get(&f.q, &q[..121], lane)','get(&f.q, if cp.dn{&q[..121]}else{&q}, lane)')
p.write_text(head+tail)
changed=subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines()
assert len(changed)==6 and all(p.startswith('src/point_add/') for p in changed),changed
patch=subprocess.check_output(['git','-C',str(source),'diff','HEAD','--','src/point_add/'])
(evidence/'candidate-n274-v1.patch').write_bytes(patch)
manifest=dict(scope='N274 prototype components only; q21 SX6, mixed22/pure24, reserve9, R23/R32 cutoff95, map4; native pending',base_revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),checkout=str(source),candidate_changed_paths=changed,protected_files_modified=False,patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p:hashlib.sha256((source/p).read_bytes()).hexdigest() for p in changed})
(evidence/'candidate-n274-v1-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
