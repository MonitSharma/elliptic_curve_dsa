"""Execute both frozen source-only cases, retaining resource failures independently."""
import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'wide-largecaps-20261016';plan=json.loads((d/'DECLARATION.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/plan['source_freeze'])==plan['source_freeze_sha256'] and sha(r/plan['input_stream'])==plan['input_stream_sha256']
assert sha(r/'target-scratch/release/product_paired_diagnostic')==plan['optimizer_executable_sha256']
env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1');results=[]
for case in plan['cases']:
    name=d/case['name'];output=Path(str(name)+'.bin');log=Path(str(name)+'-generate.log');assert not log.exists()
    env.update(EXACT_MODE='cache-retained',CACHE_ATOM_CAP=str(case['atom_cap']),ANF_PAIR_CAP='256',CACHE_PRODUCT_CAP='1000000',CACHE_RANK='density',CACHE_SPLIT='1',CACHE_EXTRA_QUBITS='64')
    with Path(str(name)+'-preflight.json').open('w') as out:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=out,check=True)
    with log.open('wb') as out:
        completed=subprocess.run(['timeout','--signal=TERM','--kill-after=30',str(plan['per_case_generation_wall_limit_seconds']),'/usr/bin/time','-v',str(r/'target-scratch/release/product_paired_diagnostic'),str(r/plan['input_stream']),str(output)],stdout=out,stderr=subprocess.STDOUT,env=env)
    row={'case':case,'generation_returncode':completed.returncode,'score':None};results.append(row)
    if completed.returncode:
        row['status']='GENERATION_RESOURCE_OR_TOOL_FAILURE_PRESERVED'
    else:
        manifest=Path(str(name)+'.manifest');mapping='=' if sha(output)==plan['input_stream_sha256'] else str(log.relative_to(r))
        manifest.write_text((r/plan['chain_manifest']).read_text()+str(output.relative_to(r))+' '+mapping+'\n')
        row['stream_sha256']=sha(output);row['proofs']={}
        for packet in ['independent','structured']:
            with Path(str(name)+f'-{packet}.log').open('wb') as out:result=subprocess.run(['/usr/bin/time','-v',str(r/'target-anchored-replay/release/product_paired_diagnostic'),plan['baseline_stream'],str(output),'+'+str(manifest),packet,str(name)+f'-{packet}.tsv'],stdout=out,stderr=subprocess.STDOUT,env=env)
            row['proofs'][packet]=result.returncode
        with Path(str(name)+'-resources.jsonl').open('w') as out:subprocess.run(['python3',str(r/'stream_resources.py'),str(output)],stdout=out,check=True)
        row['status']='ENDPOINT_GENERATED_PROOFS_PASS' if all(v==0 for v in row['proofs'].values()) else 'PROOF_FAILURE_PRESERVED'
    (d/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
print('FIXED_LARGE_CAP_CASES_TERMINAL_SEE_RESULTS',flush=True)
