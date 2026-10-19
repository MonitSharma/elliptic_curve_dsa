import hashlib,json,os,re,statistics,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'product-parent-sat-20261019/parent4-filter';ops=ws/'product-pareto-20261019/candidate-parent4/ops.bin';model=ws/'prefilter-20261015/model-source'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
prep=json.loads((r/'PREPARATION.json').read_text());assert all(sha(r/'tool'/p)==v['sha256'] for p,v in prep['files'].items())
assert sha(old/'baseline-0.jsonl')==prep['old_qualified_prefix_sha256']
reference={x['nonce']:x for x in map(json.loads,(old/'baseline-0.jsonl').open())}
bins={'frozen':old/'tool/target/release/value_prefilter','branch':r/'tool/target/release/value_prefilter'}
def run(name,mode,first,count,look,shadow=False):
    env=dict(os.environ,CANDIDATE_SEED_SHADOW='1',FAST_ZERO_DISPATCH='1',OMP_NUM_THREADS='1',RAYON_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    for key in ['PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','RAIL_SHADOW']:env.pop(key,None)
    if shadow:env.update(PACKED_ZERO_SHADOW='1',RAIL_SHADOW='1')
    with (r/(name+'.log')).open('xb') as out,(r/(name+'.err')).open('xb') as err:
        subprocess.run([str(bins[mode]),str(ops),str(first),str(count),'1',str(r/(name+'.jsonl')),str(model),str(look)],env=env,stdout=out,stderr=err,check=True)
    rows=sorted(map(json.loads,(r/(name+'.jsonl')).open()),key=lambda x:x['nonce'])
    assert len(rows)==count and rows==[reference[i] for i in range(first,first+count)],name
    assert all(not x['authoritative_rejection'] and not x['proof_accepted'] for x in rows)
    assert 'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS' in (r/(name+'.err')).read_text()
    return float(re.search(r'wall_seconds=([0-9.]+)',(r/(name+'.log')).read_text())[1])
run('partial-shadow','branch',17,11,9,True)
times={'frozen':[],'branch':[]}
for trial in range(3):
    for mode in (['frozen','branch'] if trial%2==0 else ['branch','frozen']):times[mode].append(run(f'{mode}-{trial}',mode,1,512,512))
med={k:statistics.median(v) for k,v in times.items()}
assert sha(old/'tool/target/release/value_prefilter')==prep['baseline_binary_sha256']
result={'status':'DISABLED_PREFIX_ROWS_IDENTICAL_AFTER_EXACT_ADVISORY_CHANGE','timing_nonces_per_trial':512,'threads':1,'times_seconds':times,'median_seconds':med,'end_to_end_prefix_speedup':med['frozen']/med['branch'],'all_rows_match_qualified_parent4_prefix':True,
 'partial_zeroMR_and_scalar_advisory_shadow':True,'own_Fiat_prefix_controls_pass':True,'baseline_binary_unchanged':True,'new_binary_sha256':sha(bins['branch']),'authoritative_rejection':False,'nonce_selected':None,
 'scope':'Runtime-only diagnostic on the already gate-eligible frozen parent4 source. No new circuit, statistical gate, score or operational runtime acceptance. Full new-source qualification remains mandatory before production use.'}
(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
