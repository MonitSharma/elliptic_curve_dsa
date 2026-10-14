"""Exact modular consistency of saved outputs, not a claim about hidden wires."""
from pathlib import Path
import collections, json, re
out=Path(__file__).parent;raw=out.parents[2]/'research-output/overnight-20261014/product'
e=raw/'b3-arithmetic-compare'
p=2**256-2**32-977
packets={}
for name,mode in [('known-official-failures.tsv','official_known_bad'),('../b3-paired/independent.tsv','independent')]:
 for line in(e/name).read_text().splitlines():
  if line.startswith('#'):continue
  f=line.split();packets[(mode,int(f[0]))]=list(map(lambda s:int(s,16),f[1:7]))
rows=[];counts=collections.defaultdict(collections.Counter)
for line in(e/'run.log').read_text().splitlines():
 if not line.startswith('B3_STAGE_SHOT '):continue
 f=dict(re.findall(r'(\w+)=(\S+)',line));stage=f['stage'];mode=f['mode'];i=int(f['index']);tx,ty,ax,ay,ex,ey=packets[(mode,i)]
 x,y=int(f['x'],16),int(f['y'],16)
 slope=(ty-ay)*pow((tx-ax)%p,-1,p)%p
 assert(ex,ey)==((slope*slope-tx-ax)%p,(slope*(ax-ex)-ay)%p)
 if (x,y)==(ex,ey):counts[(stage,mode)]['correct']+=1;continue
 den=(ax-x)%p
 implied=None if den==0 else (y+ay)*pow(den,-1,p)%p
 square=(x+tx+ax)%p
 same=implied is not None and implied*implied%p==square
 counts[(stage,mode)]['wrong']+=1
 counts[(stage,mode)]['consistent_single_scalar'if same else'inconsistent_single_scalar']+=1
 rows.append({'stage':stage,'mode':mode,'index':i,'x_correct':x==ex,'y_correct':y==ey,'output_consistent_with_single_scalar_and_unchanged_original_x':same,
 'expected_slope':hex(slope),'slope_implied_from_y_and_returned_x':None if implied is None else hex(implied),'slope_square_implied_from_x':hex(square),
 'implied_slope_matches_reference':implied==slope,'implied_slope_is_negative_reference':implied is not None and implied==(-slope)%p})
result={'scope':'Pure modular identities on saved output points; no access to actual divider/square/multiply wires, no phase or causal proof, no score.',
 'identity':'lambda_y=(got_y+offset_y)/(offset_x-got_x); lambda_square_x=got_x+target_x+offset_x; compare lambda_y² modp to lambda_square_x.',
 'assumption':'Consistency test assumes retained original target_x/offset_x values in the point-add formula. A mismatch can arise from altered denominator, differing scalar values or errors downstream; it does not uniquely localize the bug.',
 'counts':{f'{s}:{m}':dict(v)for(s,m),v in counts.items()},'wrong_outputs':rows}
(out/'b3-scalar-consistency.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
print(json.dumps(result['counts'],indent=2))
