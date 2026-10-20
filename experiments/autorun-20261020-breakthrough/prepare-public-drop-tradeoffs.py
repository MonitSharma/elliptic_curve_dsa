from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-acd0-exact-width-20261020';r=a.parent/'breakthrough-public-drop-tradeoffs-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','additional-tests.rs','phase-compare-compact.rs']:shutil.copyfile(old/n,r/n)
s=(old/'prepare.py').read_text();needle='"cap1233-t21"=>Some((1233,21))';assert s.count(needle)==1;s=s.replace(needle,needle+',"cap1233-rmin"=>Some((1233,21)),"cap1233-r1"=>Some((1233,21)),"cap1233-r2"=>Some((1233,21)),"cap1233-r9"=>Some((1233,21))')
needle='std::env::set_var("STACK_DROP130_RESEARCH",if config.is_some_and(|(cap,_)|cap<1234){"1"}else{"0"});';assert s.count(needle)==1;s=s.replace(needle,needle+'std::env::set_var("STACK_REVERSE_DROP_PROFILE",mode.strip_prefix("cap1233-").unwrap_or("t21"));')
needle="assert all(sha(t/p)==h for p,h in protected.items());prior=";assert s.count(needle)==1
extra=r'''p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'fn y28_drop(t: usize, rev: bool) -> usize {';assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'\n    if rev&&std::env::var("STACK_DROP130_RESEARCH").is_ok_and(|v|v=="1"){if let Some(d)=public_reverse_drop_profile(&std::env::var("STACK_REVERSE_DROP_PROFILE").unwrap_or_default(),t){return d;}}');raw+=(r/'drop-policy-tests.rs').read_bytes();p.write_bytes(raw)
'''
s=s.replace(needle,extra+needle);s=s.replace("['public','cap1234-t21','cap1233-t21','cap1232-t21','cap1233-t28']","['public','cap1233-t21','cap1233-rmin','cap1233-r1','cap1233-r2','cap1233-r9']");ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text();needle=";assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build'";assert s.count(needle)==1;s=s.replace(needle,";assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','public_reverse_drop_policy_tests','--','--nocapture','--test-threads=1'],'drop-policy-tests')==0;assert 'test result: ok. 1 passed; 0 failed;'in(r/'drop-policy-tests.log').read_text()"+needle);ast.parse(s);(r/'run.py').write_text(s)
(r/'drop-policy-tests.rs').write_text('''
fn public_reverse_drop_profile(profile:&str,t:usize)->Option<usize>{if !(124..127).contains(&t){return None;}let values=match profile{"rmin"=>[1,2,3],"r1"=>[0,1,3],"r2"=>[0,2,3],"r9"=>[1,2,2],_=>return None};Some(values[t-124])}
#[cfg(test)]mod public_reverse_drop_policy_tests{use super::*;
 #[test]fn only_declared_reverse_profiles_change_and_keep_original_forward_policy(){
  std::env::remove_var("STACK_DROP130_RESEARCH");std::env::remove_var("STACK_REVERSE_DROP_PROFILE");let base:Vec<_>=(0..145).flat_map(|t|[y28_drop(t,false),y28_drop(t,true)]).collect();
  for on in[false,true]{for(profile,values)in[("t21",None),("rmin",Some([1,2,3])),("r1",Some([0,1,3])),("r2",Some([0,2,3])),("r9",Some([1,2,2]))]{std::env::set_var("STACK_DROP130_RESEARCH",if on{"1"}else{"0"});std::env::set_var("STACK_REVERSE_DROP_PROFILE",profile);for t in 0..145{for rev in[false,true]{let expected=if on&&rev&&(124..127).contains(&t)&&values.is_some(){values.unwrap()[t-124]}else if on&&((!rev&&(130..137).contains(&t))||(rev&&(124..127).contains(&t))){3}else{base[2*t+usize::from(rev)]};assert_eq!(y28_drop(t,rev),expected);}}}}
  std::env::remove_var("STACK_DROP130_RESEARCH");std::env::remove_var("STACK_REVERSE_DROP_PROFILE");
 }
}
''')
(r/'PLAN.md').write_text('''# Exact carry-drop cost tradeoffs at complete width1233

The initial width port always asks for drop3 at reverse124/125/126. That keeps
workspace small, but exact dropped-carry regeneration can cost more T than
shedding another ordinary ripple helper. Compare fixed exact profiles before
new point inputs: original3/3/3;1/2/3;0/1/3;0/2/3;1/2/2. Forward130 drop3 stays.
Original public3d7c and prior1233/52a0 full controls precede variants. Comparator
4, plan/admission/phasefault4 and independent bounded-policy truth-table1 must
pass first. Every original y16/fold-budget/adjacentdrop/cap guard remains.
Sameparent21bit witness, windows/rounds/onefold tick ranges and whole generic
pipeline. Only exact workspace schedules vary; no packet/nonce selection.
Failure to construct is retained. Static costs are diagnostics, not scores.
Promising complete resource source needs fresh regenerated exact caches and
own finalgate against exactcurrent public product, qualifiedascendingnonce,
unchanged9024benchmark/localreview before auto official submission.
''');print(r)
