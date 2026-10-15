"""Independently count all declared failure lanes from the preserved raw censuses."""
from pathlib import Path
import gzip,hashlib,json,tarfile
base=Path(__file__).resolve().parents[2]/'experiments/product-exact-20261015'
report=json.loads((base/'repair53-native-20261016/PER_SHOT_FAILURE_COMPARISON.json').read_text())
with tarfile.open(base/'evidence.tar.gz') as archive:
    data=[]
    for source in ['parent','candidate']:
        packed=archive.extractfile(f'evidence/repair53-native-20261016/{source}-census.jsonl.gz').read()
        raw=gzip.decompress(packed)
        assert hashlib.sha256(raw).hexdigest()==report[f'{source}_rows_sha256']
        rows=list(map(json.loads,raw.splitlines()))
        assert len(rows)==32768 and [r['batch'] for r in rows]==list(range(32768))
        assert all(r['shots']==64 and not r['skipped'] for r in rows)
        for r in rows:
            assert len({f['lane'] for f in r['failures']})==len(r['failures'])
            assert all(0<=f['lane']<64 for f in r['failures'])
            for category in ['value','phase','dirty']:
                assert sum(bool(f[category]) for f in r['failures'])==r[f'{category}_shots']
        data.append(rows)
result={}
for category in ['all','value','phase','dirty']:
    sets=[]
    for rows in data:
        sets.append({(r['batch'],f['lane']):(f['k1'],f['k2']) for r in rows for f in r['failures'] if category=='all' or f[category]})
    p,c=sets
    assert all(p[k]==c[k] for k in p.keys()&c.keys())
    values={'parent_failed_shots':len(p),'candidate_failed_shots':len(c),'parent_only_failed_shots':len(p.keys()-c.keys()),'candidate_only_failed_shots':len(c.keys()-p.keys()),'same_failure_lanes':len(p.keys()&c.keys())}
    assert values==report['categories'][category]
    result[category]=values
assert result['value']['parent_only_failed_shots']==14 and result['value']['candidate_only_failed_shots']==0
out={'status':'INDEPENDENT_ALL_DECLARED_RAW_FAILURE_LANES_MATCH','batches_per_source':32768,'shots_per_source':2097152,'categories':result,'no_extra_inputs_or_source_changes':True,'not_a_complete_benchmark_or_universal_repair_claim':True}
(base/'repair53-native-20261016/ROOT_FAILURE_LANES_VERIFIED.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
