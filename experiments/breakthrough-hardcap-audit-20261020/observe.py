import hashlib,json,os,subprocess
from collections import Counter
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();results={}
for cap,expected in f['controls'].items():
    env=os.environ.copy();env['BREAK_CAP']=cap
    with(r/f'cap{cap}.out').open('xb')as out,(r/f'cap{cap}.log').open('xb')as err:
        subprocess.run([str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err,check=True)
    assert sha(t/'ops.bin')==expected
    water=Counter();contracts=[]
    for line in(r/f'cap{cap}.log').read_text().splitlines():
        if line.startswith('HIGH_WATER\t'):
            phase,op,active,next_id,caller=line.split('\t')[1:];water[(phase,caller,int(active))]+=1
        if line.startswith('RIPPLE_CONTRACT\t'):
            values=list(map(int,line.split('\t')[1:]));contracts.append(dict(zip(['op','width','source_bits','active','full_c0','full_c1','deferred','known_output','known_terminal','borrowed','copy_request','carry_out'],values)))
    results[cap]={'raw_sha256':expected,'high_water_sites':[{'phase':p,'caller':c,'active':a,'occurrences':n}for(p,c,a),n in sorted(water.items())],
        'ripple_contracts':contracts}
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
(r/'HARD-CAP-AUDIT.json').write_text(json.dumps({'status':'BOTH_COMPLETE_RAW_STREAMS_BYTE_IDENTICAL','controls':results,'scope':'Source allocator and ripple-contract audit only; no new score.'},indent=2)+'\n')
for cap,v in results.items():print(cap,json.dumps(v['high_water_sites']))
