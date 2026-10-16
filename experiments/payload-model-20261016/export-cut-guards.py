from pathlib import Path
import csv,json,hashlib,itertools
root=Path(__file__).resolve().parent
src=Path('/home/hclau/ecdsa_research/product-exact-20261015/tip/src/point_add')
out=[];deleted=0;tests=0
for line in (src/'census_cut_data.txt').read_text().splitlines():
 if not line.strip()or line.startswith('#'):continue
 site,kind,c2,c1,target,cc,action=line.split();site,c2,c1,target=map(int,[site,c2,c1,target]);survivor=removed='';phase_only=kind=='ccz'
 if action.startswith('cx:'):
  survivor=int(action.split(':')[1]);assert survivor in(c1,c2);removed=c2 if survivor==c1 else c1;predicate=f'q{survivor} & !q{removed}'
 elif action=='del':predicate=f'q{c1} & q{c2}'+(f' & q{target}'if phase_only else'')
 else:predicate='unhandled';assert False,action
 if cc!='-':predicate=f'bit{cc} & ({predicate})'
 # Every possible local control and enclosing classical base value. This
 # proves the per-edit Boolean lemma independently of any model wire mapping.
 wires=sorted(set([c1,c2,target]+([survivor]if survivor!=''else[])))
 for assignment in itertools.product([0,1],repeat=len(wires)+1):
  v=dict(zip(wires,assignment));cond=assignment[-1]
  old=cond&v[c1]&v[c2]&(v[target] if phase_only else 1)
  new=0 if action=='del'else cond&v[survivor]
  guard=cond&(v[c1]&v[c2]if action=='del'else v[survivor]&(1-v[removed]))
  assert guard==(old^new)
  if guard==0:assert old==new
  tests+=1
 out.append(dict(row=len(out),site=site,finalsite=site-deleted,kind=kind,c2=c2,c1=c1,target=target,condition=cc,action=action,survivor=survivor,removed_control=removed,phase_only=phase_only,predicate=predicate))
 deleted+=action=='del'
with open(root/'cut-guards.csv','w',newline='')as f:
 writer=csv.DictWriter(f,fieldnames=list(out[0]));writer.writeheader();writer.writerows(out)
(root/'cut-guard-lemma.json').write_text(json.dumps({'rows':len(out),'deleted':deleted,'reduced':len(out)-deleted,'truth_assignments_checked':tests,'phase_only_rows':sum(r['phase_only']for r in out),'source_sha256':hashlib.sha256((src/'census_cut_data.txt').read_bytes()).hexdigest(),'status':'EXACT_LOCAL_LEMMA; MODEL_TO_INTERNAL_WIRE_MAPPING_NOT_PROVED'},indent=2)+'\n')
print('exported',len(out),'source-bound guards;',tests,'local truth assignments')
