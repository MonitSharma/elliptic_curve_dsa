from pathlib import Path
import subprocess,shutil,json,hashlib
r=Path('/home/hclau/ecdsa_research/seam-phase-repair-20261016');tip=r.parent/'product-exact-20261015/tip';dest=r/'candidate';rev=json.loads((r/'PREDECLARED.json').read_text())['source_revision']
assert json.loads((r/'region.json').read_text())['admission']=='B'
(r/'base-status.txt').write_bytes(subprocess.check_output(['git','-C',str(tip),'status','--short']))
assert subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip()==rev
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(dest),rev],check=True)
for name in['front_seam.rs','front_seam.bin']:shutil.copy2(r/name,dest/'src/point_add'/name)
p=dest/'src/point_add/mod.rs';s=p.read_text();needle='    ops = apply_tail_nonce(ops, nonce);';assert s.count(needle)==1;p.write_text('mod front_seam;\n'+s.replace(needle,needle+'\n    ops = front_seam::run(ops);'))
subprocess.run(['git','-C',str(dest),'add','-N','src/point_add/front_seam.rs','src/point_add/front_seam.bin'],check=True)
(r/'candidate-source.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(r/'candidate-source.json').write_text(json.dumps(dict(base=rev,source_changes_only_point_add=True,all_original_tables_and_assertions_retained=True,admission=json.loads((r/'ADMISSION-B.json').read_text()),files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()},protected={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[dest/'Cargo.toml',dest/'Cargo.lock',dest/'rust-toolchain.toml',dest/'src/circuit.rs',dest/'src/sim.rs',dest/'src/curve.rs',dest/'src/bin/build_circuit.rs',dest/'src/bin/eval_circuit.rs',dest/'src/lib.rs']if p.exists()}),indent=2)+'\n')
(r/'guard-tests.rs').write_text('#[path="candidate/src/circuit.rs"] mod circuit;\n#[path="front_seam.rs"] mod front_seam;\n')
