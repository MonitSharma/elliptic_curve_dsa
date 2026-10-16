"""Predeclared fresh cache recipes on the uniformly corrected source, never old leases."""
import copy,hashlib,json,os,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair-cache53-20261016';d.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=r.parent/'precision-family-20261016/candidate';original=source/'ops.bin';inputhash='1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522'
assert sha(original)==inputhash
stages=copy.deepcopy(json.loads((r/'PRODUCT53_FREEZE.json').read_text())['stages']);assert len(stages)==53
plan={'source':'precision-family-20261016/candidate/ops.bin','source_sha256':inputhash,'source_base_revision':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),'scope':'New correctness-improving29-fold precision family, followed by exact cache rewrites. Every lease is rederived from the changed source, never reused from original4b. This is not resampling the failed original53 gate.','stage_count':53,'stages':stages,'checkpoints':[25,53],'proof':'For each checkpoint,512 full anchored original-repair-versus-cache state/classical/phase/scratch comparisons. Exact rewrite proofs compare with repair parent; eligibility must compare final composite against original4b.','qualification':'Final native source must reproduce exact frozen stream; fresh candidate-versus-original4b fixed32768 batches required before any nonce search. Repair-parent gate alone is insufficient. Include every declared row, no interim selection.','resources':{'analysis_threads':1,'address_limit_GiB':20},'score':None,'nonce_search_performed':False}
(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
frozen=d/'input-1cd3457b.bin';shutil.copy2(original,frozen);assert sha(frozen)==inputhash
shutil.copytree(source/'src/point_add',d/'repair-point-add-source',dirs_exist_ok=False)
(d/'repair-source-files.json').write_text(json.dumps({str(p.relative_to(d/'repair-point-add-source')):sha(p) for p in (d/'repair-point-add-source').rglob('*') if p.is_file()},indent=2)+'\n')
with (d/'input-prefix-manifest.jsonl').open('w') as out:subprocess.run(['python3',str(r/'stream_prefix_manifest.py'),str(frozen)],stdout=out,check=True)
manifest=d/'chain.manifest';manifest.write_text('');previous=frozen;env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
for i,spec in enumerate(stages,1):
    mode='cache' if spec['family']=='affine' else 'cache-'+spec['family'];name=d/f"repair-{i:02d}-{spec['family']}-{spec['atom_cap']}";output=Path(str(name)+'.bin');log=Path(str(name)+'-generate.log')
    env.update(EXACT_MODE=mode,CACHE_ATOM_CAP=str(spec['atom_cap']),ANF_PAIR_CAP=str(spec['pair_cap']),CACHE_PRODUCT_CAP=str(spec['product_cap']),CACHE_SPLIT='1',CACHE_RANK=spec['rank'])
    with Path(str(name)+'-preflight.json').open('w') as out:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=out,check=True)
    with log.open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-flags/release/product_paired_diagnostic'),str(previous),str(output)],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
    mapping='=' if sha(output)==sha(previous) else str(log.relative_to(r))
    with manifest.open('a') as out:out.write(str(output.relative_to(r))+' '+mapping+'\n')
    with (d/'streams.sha256').open('a') as out:out.write(sha(output)+' '+str(output.relative_to(r))+'\n')
    previous=output
    if i in [25,53]:
        checkpoint=d/f'stage-{i}.manifest';shutil.copy2(manifest,checkpoint)
        for packet in ['independent','structured']:
            with (d/f'stage-{i}-{packet}.log').open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-anchored-replay/release/product_paired_diagnostic'),str(frozen),str(previous),'+'+str(checkpoint),packet,str(d/f'stage-{i}-{packet}.tsv')],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
        with (d/f'stage-{i}-resources.jsonl').open('w') as out:subprocess.run(['python3',str(r/'stream_resources.py'),str(previous)],stdout=out,check=True)
print(json.dumps({'status':'FIXED53_GENERATION_AND512_STATE_PHASE_PROOFS_PASS','source_sha256':inputhash,'final_stream':str(previous.relative_to(r)),'final_sha256':sha(previous),'native_source_port':'pending','fresh_original4b_gate':'pending','score':None}),flush=True)
