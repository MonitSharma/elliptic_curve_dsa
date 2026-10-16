"""Run all56 declared source-only stages, then the sole final151 replay."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'wide-to151-rank-20261016';plan=json.loads((d/'DECLARATION.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/plan['source_freeze'])==plan['source_freeze_sha256'] and sha(r/plan['input_stream'])==plan['input_stream_sha256']
manifest=d/'chain.manifest';assert not manifest.exists();base=json.loads((r/plan['source_freeze']).read_text());shutil.copy2(r/base['chain_manifest'],manifest)
previous=r/plan['input_stream'];env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
for i,spec in enumerate(plan['stages'][95:],96):
    name=d/f"wide-{i}-{spec['family']}-{spec['atom_cap']}-{spec['rank']}";output=Path(str(name)+'.bin');log=Path(str(name)+'-generate.log')
    env.update(EXACT_MODE='cache-'+spec['family'],CACHE_ATOM_CAP=str(spec['atom_cap']),ANF_PAIR_CAP='64',CACHE_PRODUCT_CAP='1000000',CACHE_SPLIT='1',CACHE_RANK=spec['rank'])
    with Path(str(name)+'-preflight.json').open('w') as out:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=out,check=True)
    with log.open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-flags/release/product_paired_diagnostic'),str(previous),str(output)],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
    mapping='=' if sha(output)==sha(previous) else str(log.relative_to(r))
    with manifest.open('a') as out:out.write(str(output.relative_to(r))+' '+mapping+'\n')
    with (d/'streams.sha256').open('a') as out:out.write(sha(output)+' '+str(output.relative_to(r))+'\n')
    previous=output
    if i==151:
        checkpoint=d/'stage-151.manifest';shutil.copy2(manifest,checkpoint)
        for packet in ['independent','structured']:
            with (d/f'stage-151-{packet}.log').open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-anchored-replay/release/product_paired_diagnostic'),plan['baseline_stream'],str(previous),'+'+str(checkpoint),packet,str(d/f'stage-151-{packet}.tsv')],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
        with (d/'stage-151-resources.jsonl').open('w') as out:subprocess.run(['python3',str(r/'stream_resources.py'),str(previous)],stdout=out,check=True)
print('FIXED151_GENERATION_AND_FINAL512_REPLAY_PASS',flush=True)
