from pathlib import Path
import json,collections
r=Path(__file__).parent;e=r/'evidence';m=json.load(open(e/'width-lifetime-tip.json'));dep={v['start']:v['entry_depth']for v in m['all_spans']};contracts=json.load(open(e/'width-contract-tip.json'));expected=json.load(open(e/'width-scope-correction-v1.json'))
for result,name in zip(expected['strict_results'],['width-affine-tip.json','width-affine-cap128-tip.json','width-affine-cap512-tip.json']):
 a=json.load(open(e/name));queries={v['start']:v for v in a['all_spans']};counts=collections.Counter();cost=0;unknown=[];blocked=[]
 for v in contracts['all_spans']:
  has=queries[v['start']]['relation']is not None
  if has and dep[v['start']]==0:counts['GLOBAL_ENTRY_AFFINE_LOAN_QUERY']+=1
  elif v['accepted']:counts[v['family']]+=1;cost+=v['delta_T_static_unconditional']
  else:unknown.append(v['start'])
  if has and dep[v['start']]>0:blocked.append(v['start'])
 assert dict(counts)==result['strict_counts']and cost==result['paid_T']and unknown==result['unresolved_starts']and blocked==result['conditional_entry_starts']
print('STRICT_WIDTH_SCOPE_COUNTS_REPRODUCED; noQ1233claim')
