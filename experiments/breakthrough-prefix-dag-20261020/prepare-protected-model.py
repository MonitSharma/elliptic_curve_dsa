from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'schedule-model.py').read_text();a="names=list(f)[15:46];assert len(names)==31";assert s.count(a)==1;s=s.replace(a,a+"\nprotect=os.environ['PREFIX_PROTECT'];protected_names=protect.split('+');assert all(n in names for n in protected_names);protected_masks=[d['helper_masks'][names.index(n)]for n in protected_names]")
a='mask=(1<<(15+born))-1;req=[v&mask for v in desired]';assert s.count(a)==1;s=s.replace(a,'mask=(1<<(15+born))-1;req=[v&mask for v in desired+protected_masks]')
a="'delayed_garbage':garbage.copy(),'erasures':erasures";assert s.count(a)==1;s=s.replace(a,"'delayed_garbage':garbage.copy(),'retained_masks':held.copy(),'full_masks':full.copy(),'erasures':erasures")
a='finishing=[];quad_final_helpers=len(held)-15';assert s.count(a)==1;terminal='''req,_=independent(desired);full,_=independent(req+held);garbage=full[len(req):];erasures=[]
while garbage:
 choices=[]
 for g in garbage:
  w=quadratic_witness(g,req+[v for v in garbage if v!=g])
  if w is not None:choices.append((len(w),g,w))
 if not choices:break
 priority=[d['helper_masks'][names.index(n)]for n in ['t1','c5','c4','c3','c2','c1']];_,g,w=min(choices,key=lambda x:(priority.index(x[1])if x[1]in priority else len(priority),x[0],x[1]));garbage.remove(g);erasures.append({'function_mask':g,'phase_terms':w})
held=req+garbage;reports.append({'born':31,'cleanup_only':True,'retained_physical_wires':len(held)-1,'delayed_garbage':garbage.copy(),'retained_masks':held.copy(),'full_masks':full.copy(),'erasures':erasures})
finishing=[];quad_final_helpers=len(held)-15''';s=s.replace(a,terminal)
s=s.replace("'basis_strategy':basis_strategy,'erase_strategy':erase_strategy", "'basis_strategy':basis_strategy,'erase_strategy':erase_strategy,'protected_function':protect")
s=s.replace('assert len(requirements[-1])==35','assert 35<=len(requirements[-1])<=35+len(protected_names)')
s=s.replace("output='SCHEDULE-v2-'+basis_strategy+'-'+erase_strategy+'.json'", "output='PROTECTED-v3-'+protect+'.json'")
(r/'protected-schedule-model.py').write_bytes(s.encode())
