"""Run the separately frozen95-stage continuation after coordinator priority release."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
family=sys.argv[1] if len(sys.argv)>1 else 'product';assert family in ['product','wide']
r=Path(__file__).resolve().parent;d=r/f'{family}-to95-rank-20261016';plan=json.loads((d/'DECLARATION.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/plan['source_freeze'])==plan['source_freeze_sha256'];assert sha(r/plan['input_stream'])==plan['input_stream_sha256'];assert not (d/'chain.manifest').exists()
manifest=d/'chain.manifest';base=json.loads((r/plan['source_freeze']).read_text());shutil.copy2(r/base['chain_manifest'],manifest);previous=r/plan['input_stream'];env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
for i,spec in enumerate(plan['stages'][67:],68):
    name=d/f"{family}-{i}-{spec['family']}-{spec['atom_cap']}-{spec['rank']}";output=Path(str(name)+'.bin');log=Path(str(name)+'-generate.log')
    env.update(EXACT_MODE='cache-'+spec['family'],CACHE_ATOM_CAP=str(spec['atom_cap']),ANF_PAIR_CAP='64',CACHE_PRODUCT_CAP='1000000',CACHE_SPLIT='1',CACHE_RANK=spec['rank'])
    with Path(str(name)+'-preflight.json').open('w') as out:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=out,check=True)
    with log.open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-flags/release/product_paired_diagnostic'),str(previous),str(output)],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
    mapping='=' if sha(output)==sha(previous) else str(log.relative_to(r))
    with manifest.open('a') as out:out.write(str(output.relative_to(r))+' '+mapping+'\n')
    with (d/'streams.sha256').open('a') as out:out.write(sha(output)+' '+str(output.relative_to(r))+'\n')
    previous=output
    if i in plan['checkpoints']:
        checkpoint=d/f'stage-{i}.manifest';shutil.copy2(manifest,checkpoint)
        for packet in ['independent','structured']:
            with (d/f'stage-{i}-{packet}.log').open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-anchored-replay/release/product_paired_diagnostic'),str(r/plan.get('baseline_stream','tip/ops.bin')),str(previous),'+'+str(checkpoint),packet,str(d/f'stage-{i}-{packet}.tsv')],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
        with (d/f'stage-{i}-resources.jsonl').open('w') as out:subprocess.run(['python3',str(r/'stream_resources.py'),str(previous)],stdout=out,check=True)
print('FIXED95_GENERATION_AND_ALL_CHECKPOINTS_PASS',flush=True)
