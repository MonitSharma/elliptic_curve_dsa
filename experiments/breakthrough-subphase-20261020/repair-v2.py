"""Preserve an invalid const HashMap initializer and use runtime thread-local init."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer'
assert(r/'run.exit').read_text().strip()=='101'
failed=r/'failed-compile-v1';failed.mkdir(exist_ok=False)
for name in['prepare.py','build.log','SOURCE_FREEZE.json','source.patch','run.exit']:
 shutil.copyfile(r/name,failed/name)
p=t/'src/point_add/leapfrog.rs';shutil.copyfile(p,failed/'leapfrog.rs')
raw=p.read_bytes();old=b'= const { std::cell::RefCell::new(std::collections::HashMap::new()) };'
assert raw.count(old)==1;raw=raw.replace(old,b'= std::cell::RefCell::new(std::collections::HashMap::new());');p.write_bytes(raw)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text());assert all(sha(t/name)==v for name,v in freeze['protected_files'].items())
freeze['source_files']={p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()}
freeze['repair']='Initialize the random-seeded diagnostic HashMap at runtime, not in a const block; circuit construction unchanged.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(freeze,indent=2)+'\n')
(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
env=os.environ.copy();env['BREAK_CAP']='1234'
def run(args,cwd,output,error):
 with(r/output).open('xb')as out,(r/error).open('xb')as err:
  proc=subprocess.run(args,cwd=cwd,env=env,stdout=out,stderr=err)
 assert proc.returncode==0,(args,proc.returncode)
try:
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],t,'build-v2.out','build-v2.log')
 run(['/usr/bin/time','-v',str(t/'target/release/build_circuit')],t,'generate.out','generate.log')
 run(['python3',str(r/'segments.py')],r,'segments.log','segments.err')
 env['PHASE_MAP']=str(r/'segment-map.tsv')
 run(['/usr/bin/time','-v',str(r.parent/'breakthrough-profile-20261020/tool/target/release/phase-replay'),str(t/'ops.bin'),'breakthrough-raw-subphase-cost-v1','0','512','2',str(r/'region-census.jsonl'),'8'],r,'replay.out','replay.err')
 assert all(sha(t/name)==v for name,v in{**freeze['source_files'],**freeze['protected_files']}.items())
except BaseException:
 (r/'run-v2.exit').write_text('1\n');raise
else:(r/'run-v2.exit').write_text('0\n')
