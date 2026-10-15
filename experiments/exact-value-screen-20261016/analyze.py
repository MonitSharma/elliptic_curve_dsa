from pathlib import Path
import collections,json,re,statistics
root=Path(__file__).resolve().parent
def load(name):return {r['nonce']:r for r in map(json.loads,(root/(name+'.jsonl')).read_text().splitlines())}
baseline=load('compare-1-original');assert sorted(baseline)==list(range(1,1025))
reports={}
for trial in range(1,4):
 for mode in ['original','value']:
  name=f'compare-{trial}-{mode}';data=load(name);assert sorted(data)==list(range(1,1025))
  assert all(data[n]['pass']==baseline[n]['pass'] and data[n]['kind']==baseline[n]['kind'] and data[n]['exact_witness_batch']==baseline[n]['exact_witness_batch'] for n in data)
  text=(root/(name+'.log')).read_text();m=re.search(r'wall_seconds=([0-9.]+).*preparation_seconds=([0-9.]+).*confirmation_seconds=([0-9.]+)',text);assert m
  report=dict(zip(['wall_seconds','preparation_seconds','confirmation_seconds'],map(float,m.groups())))
  report['mean_selected_rng_group_seconds']=statistics.mean(r['selected_rng_group_secs'] for r in data.values())
  report['mean_selected_exact_group_seconds']=statistics.mean(r['selected_exact_group_secs'] for r in data.values())
  reports[name]=report
assert all(not r['pass'] for r in baseline.values())
positive=load('positive');p=positive[1046072871510];assert p['pass'] and p['batches_run']==141
assert 'ok=true shots=9024 classical=0 phase=0 ancilla=0' in (root/'positive.log').read_text()
partial=load('partial');assert sorted(partial)==list(range(17,28))
assert all(partial[n]['pass']==baseline[n]['pass'] and partial[n]['kind']==baseline[n]['kind'] for n in partial)
medians={mode:statistics.median(reports[f'compare-{t}-{mode}']['wall_seconds'] for t in range(1,4)) for mode in ['original','value']}
out={'status':'EXACT_VALUE_PREFILTER_DIFFERENTIAL_PASS_FIXED_TIMING_COMPLETE','source':'2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e','predetermined_nonces':1024,'all_rejected':True,'truth_and_witness_equal_to_original':True,'positive_control':{'nonce':1046072871510,'batches':141,'protected_replay_shots':9024,'all_channels_zero':True},'partial_range':[17,27],'full_word_shadow':'all q/b words on128 nonces, every positive-control batch and partial range; original measurement RNG retained','runs':reports,'median_wall_seconds':medians,'relative_speedup':medians['original']/medians['value'],'global_rng_independence_assumed':False,'nonce_search_performed':False,'resource_record':False}
(root/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
