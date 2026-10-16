import hashlib,json,os,struct,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parent;os.chdir(R)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((R/'BASE-BINDING.json').read_text());source=Path(b['stream_path'])
assert sha(source)==b['stream_sha256']
available=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))
assert available>=130023424, '24GiB workload plus100GiB reserve required'
env=os.environ.copy();env.update(CARGO_BUILD_JOBS='1',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
cargo='/home/hclau/.cargo/bin/cargo'
with (R/'tests.log').open('w')as f:subprocess.run([cargo,'test','--manifest-path','tool/Cargo.toml','--release','--locked','--offline','--bin','all70_rng_mask','--','--test-threads=1'],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
with (R/'build.log').open('w')as f:subprocess.run([cargo,'build','--manifest-path','tool/Cargo.toml','--release','--locked','--offline','--bin','all70_rng_mask'],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
paths=[p for p in(R/'tool').rglob('*')if p.is_file()and'target'not in p.parts]+[R/'tool/target/release/all70_rng_mask',source,R/'BASE-BINDING.json',R/'SOURCE-PLAN.json',R/'PREPARED-SOURCE.json',R/'prepare.py',R/'run.py',R/'run.sh',R/'reset-hints.json',R/'candidates.json',R.parent/'prefilter-20261015/packets/audit.tsv']
before={str(p):sha(p)for p in paths};(R/'BEFORE-PINS.json').write_text(json.dumps(before,indent=2)+'\n')
start=time.monotonic()
with (R/'global.json').open('w')as out,(R/'global.log').open('w')as err:
 p=subprocess.run(['timeout','--signal=TERM','--kill-after=10','900','/usr/bin/time','-v','prlimit','--as=25769803776','--','tool/target/release/all70_rng_mask',str(source),str(R.parent/'prefilter-20261015/packets/audit.tsv'),'32','reset-hints.json'],env=env,stdout=out,stderr=err)
after={str(p):sha(p)for p in paths};(R/'AFTER-PINS.json').write_text(json.dumps(after,indent=2)+'\n');assert before==after
result={'proof_exit':p.returncode,'elapsed_s':time.monotonic()-start,'source_before_after_equal':True,'authority':False}
if p.returncode==0:
 report=json.loads((R/'global.json').read_text());assert report['output_bits']==512 and report['symbolic_input_wires']==1024
 assert report['protected_full_state_containment_seeds']==4 and report['rng_draws']==906156
 result.update(mask_nodes=report['mask_nodes'],concrete_known_output_bits=report['concrete_known_output_bits'],unresolved_rng_dependent_bits=report['unresolved_rng_dependent_bits'])
 data=(R/'mr-mask-all70.bin').read_bytes();assert data[:8]==b'MRMASK01'
 nodes,np,nr=struct.unpack_from('<3Q',data,8);assert(np,nr)==(1024,512)and len(data)==32+16*nodes+4*nr
 roots=struct.unpack_from('<512I',data,32+16*nodes)
 result['root_summary']={'constant0_known':roots.count(0),'constant1_unknown':roots.count(1),'nonconstant':sum(x>1 for x in roots)}
 if any(x!=1 for x in roots):
  validator=R.parent/'prefilter-20261015/tool/target/release/mask_validate'
  fixtures={'audit':'56bd53b84fa65d28779f7cbb28b1b969453ca1da695e46392a90b00abba23ba3','all-failing-tip':'7ea58bb492c82ff8d9b194a97ba097d5449acda8302539c67f746413760c1efb'}
  assert sha(validator)=='e5147722a4273ed3ffc6dfdb97af5890bb9cf7b90451a2f56ec6521172aa3f88'
  masksha=sha(R/'mr-mask-all70.bin')
  result['existing_fixture_validation']={}
  if nodes>=100000000:
   result['existing_fixture_validation']['status']='UNKNOWN_EXISTING_GENERIC_VALIDATOR_NODE_LIMIT_NO_EXPANSION'
  else:
   for label,h in fixtures.items():
    fixture=R.parent/f'prefilter-20261015/packets/{label}.tsv';assert sha(fixture)==h
    with(R/f'validation-{label}.json').open('w')as vo,(R/f'validation-{label}.log').open('w')as ve:
     subprocess.run([str(validator),str(source),str(R/'mr-mask-all70.bin'),str(fixture)],env=env,stdout=vo,stderr=ve,check=True)
    result['existing_fixture_validation'][label]=json.loads((R/f'validation-{label}.json').read_text())
    assert sha(fixture)==h
  assert sha(R/'mr-mask-all70.bin')==masksha and sha(source)==b['stream_sha256']
result['proof_plus_validation_elapsed_s']=time.monotonic()-start
(R/'RUN-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
raise SystemExit(p.returncode)
