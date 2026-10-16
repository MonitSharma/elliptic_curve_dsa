"""Run all14 exact stages, then final512 corrected-parent comparisons."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair-to67-rank-20261016';plan=json.loads((d/'DECLARATION.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/plan['source_freeze'])==plan['source_freeze_sha256'] and sha(r/plan['input_stream'])==plan['input_stream_sha256']
assert sha(r/plan['repair_parent_stream'])==plan['repair_parent_sha256'] and sha(r/'target-flags/release/product_paired_diagnostic')==plan['optimizer_executable_sha256']
manifest=d/'chain.manifest';assert not manifest.exists();shutil.copy2(r/plan['chain_manifest'],manifest);previous=r/plan['input_stream'];env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
for i,spec in enumerate(plan['stages'][53:],54):
    name=d/f"repair-{i}-{spec['family']}-{spec['atom_cap']}-{spec['rank']}";output=Path(str(name)+'.bin');log=Path(str(name)+'-generate.log')
    env.update(EXACT_MODE='cache-'+spec['family'],CACHE_ATOM_CAP=str(spec['atom_cap']),ANF_PAIR_CAP='64',CACHE_PRODUCT_CAP='1000000',CACHE_SPLIT='1',CACHE_RANK=spec['rank'])
    with Path(str(name)+'-preflight.json').open('w') as out:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=out,check=True)
    with log.open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-flags/release/product_paired_diagnostic'),str(previous),str(output)],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
    mapping='=' if sha(output)==sha(previous) else str(log.relative_to(r))
    with manifest.open('a') as out:out.write(str(output.relative_to(r))+' '+mapping+'\n')
    with (d/'streams.sha256').open('a') as out:out.write(sha(output)+' '+str(output.relative_to(r))+'\n')
    previous=output
checkpoint=d/'stage-67.manifest';shutil.copy2(manifest,checkpoint)
for packet in ['independent','structured']:
    with (d/f'stage-67-{packet}.log').open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-anchored-replay/release/product_paired_diagnostic'),str(r/plan['repair_parent_stream']),str(previous),'+'+str(checkpoint),packet,str(d/f'stage-67-{packet}.tsv')],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
with (d/'stage-67-resources.jsonl').open('w') as out:subprocess.run(['python3',str(r/'stream_resources.py'),str(previous)],stdout=out,check=True)
assert json.loads((d/'stage-67-resources.jsonl').read_text())['qubits']==1234
print('FIXED_REPAIRED67_GENERATION_AND512_REPLAY_PASS',flush=True)
