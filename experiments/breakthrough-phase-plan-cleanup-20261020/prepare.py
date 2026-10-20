import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';old=ws/'breakthrough-phase-plan-native-20261020';pred=ws/'breakthrough-phase-predicate-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE-v4.json').read_text());pf=json.loads((pred/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(old/'run-v4.exit').read_text().strip()=='0'and(pred/'run.exit').read_text().strip()=='0'
for source,freeze in[(old,f),(pred,pf)]:assert all(sha(source/'primitive'/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'primitive/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'primitive');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
(t/'src/point_add/phase_plan.rs').write_bytes((r/'phase_plan.rs').read_bytes());(t/'src/point_add/phase_predicate.rs').write_bytes((pred/'primitive/src/point_add/phase_predicate.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as out:out.write(b'\nmod phase_predicate;\n')
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();runtime=raw.split(b'#[cfg(test)]mod weighted_plan_tests{')[0]
def change(needle,replacement):
 global raw
 assert raw.count(needle)==1,(needle,raw.count(needle));raw=raw.replace(needle,replacement)
change(b'kept.push((lo,hi,cin,out));cin=out;',b'kept.push((lo,hi,cin,out,chunk.phase_drops.clone()));cin=out;')
change(b'for(lo,hi,cin,out)in kept.into_iter().rev(){kept_erase(c,acc,add,lo,hi,cin,out);}',b'''for(lo,hi,cin,out,pd)in kept.into_iter().rev(){
 if let Some(drops)=pd{let bit=c.alloc_bit();c.hmr(out,bit);c.release_clean(out);c.push_condition(bit);c.x_all(&acc[lo..hi]);
 let rows:Vec<_>=add[lo..hi].iter().map(|v|v.w.clone()).collect();let ones:Vec<_>=add[lo..hi].iter().map(|v|v.one).collect();
 assert!(crate::point_add::phase_predicate::apply(c,&acc[lo..hi],&rows,&ones,cin,&drops,false));c.x_all(&acc[lo..hi]);c.pop_condition();c.free_bit(bit);
 }else{kept_erase(c,acc,add,lo,hi,cin,out);}}''')
change(b'for budget in 9..=10{fixture(pattern,budget,false,false,None);',b'for budget in 8..=10{fixture(pattern,budget,false,false,None);')
change(b'for budget in[9,10]{for inverse',b'for budget in[8,9,10]{for inverse')
change(b'for(rank,expected)in[(1,[52,42,38]),(2,[64,45,38])]',b'for(rank,expected)in[(1,[105,84,76]),(2,[140,90,76])]')
change(b'assert!(phase_plan::choose(&rows,8).is_none());for(budget,&cost)in(9..=10).zip(&expected[1..])',b'assert!(phase_plan::choose(&rows,7).is_none());for(budget,&cost)in(8..=10).zip(&expected)')
raw=raw.replace(b'plan.extra_x2',b'plan.extra_x4').replace(b'p.extra_x2',b'p.extra_x4').replace(b'model_extra_x2=',b'model_extra_x4=')
assert raw.split(b'#[cfg(test)]mod weighted_plan_tests{')[0]==runtime;p.write_bytes(raw)
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'primitive/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'scope':'Weighted component schedules include exact pure-phase cleanup drops and quarter-weighted extra cost. Full budgets8/9/10 oldplan8/9 actualcore plus complete RNGposition/inverse controls. Original production prefix unchanged; component only, no point-add record/finalgate/nonce/novelty claim.'},indent=2)+'\n')
