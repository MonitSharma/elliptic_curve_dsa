from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-acd0-exact-width-20261020';r=a.parent/'breakthrough-public-acd0-exact-width-v2-20261020';r.mkdir(exist_ok=False)
for p in old.iterdir():
 if p.is_file()and p.name not in ['SOURCE-FREEZE.json','RESULT.json','PROGRESS.json']:shutil.copyfile(p,r/p.name)
p=r/'prepare.py';s=p.read_text();needle='"cap1233-t21"=>Some((1233,21)),"cap1232-t21"=>Some((1232,21)),"cap1233-t28"=>Some((1233,28))';assert s.count(needle)==1;s=s.replace(needle,needle+',"cap1231-t21"=>Some((1231,21)),"cap1232-u1"=>Some((1232,21)),"cap1231-u1"=>Some((1231,21)),"cap1232-u2"=>Some((1232,21))')
needle="std::env::set_var(\"STACK_DROP130_RESEARCH\",if config.is_some_and(|(cap,_)|cap<1234){\"1\"}else{\"0\"});";assert s.count(needle)==1;s=s.replace(needle,needle+'std::env::set_var("STACK_DROP_EARLY_RESEARCH",if config.is_some_and(|(cap,_)|cap<=1232){"1"}else{"0"});if mode.ends_with("-u1"){std::env::set_var("HEO_PIN_PP_CHUNK_SHAPE","64:1,38:1,25:-2,0:-4");}if mode.ends_with("-u2"){std::env::set_var("HEO_PIN_PP_CHUNK_SHAPE","64:2,38:2,25:-1,0:-3");}')
needle='(!rev&&(130..137).contains(&t))';assert s.count(needle)==1;s=s.replace(needle,'(!rev&&((if std::env::var("STACK_DROP_EARLY_RESEARCH").is_ok_and(|v|v=="1"){127}else{130})..137).contains(&t))')
needle="'modes':['public','cap1234-t21','cap1233-t21','cap1232-t21','cap1233-t28']";assert s.count(needle)==1;s=s.replace(needle,"'modes':['public','cap1233-t21','cap1232-t21','cap1231-t21','cap1232-u1','cap1231-u1','cap1232-u2']")
needle="+tests+b'\\n'+(r/'additional-tests.rs').read_bytes()";assert s.count(needle)==1;s=s.replace(needle,needle+"+b'\\n'+(r/'early-policy-tests.rs').read_bytes()")
ast.parse(s);p.write_text(s)
(r/'early-policy-tests.rs').write_text('''
#[cfg(test)]mod exact_early_drop_policy_tests{
 use super::*;
 #[test]fn new_early_range_retains_original_policy_and_only_selects_existing_exact_plan(){
  std::env::remove_var("STACK_DROP130_RESEARCH");std::env::remove_var("STACK_DROP_EARLY_RESEARCH");let baseline:Vec<_>=(0..145).flat_map(|t|[y28_drop(t,false),y28_drop(t,true)]).collect();
  for on in [false,true]{for early in [false,true]{std::env::set_var("STACK_DROP130_RESEARCH",if on{"1"}else{"0"});std::env::set_var("STACK_DROP_EARLY_RESEARCH",if early{"1"}else{"0"});for t in 0..145{for rev in [false,true]{let chosen=on&&((!rev&&((if early{127}else{130})..137).contains(&t))||(rev&&(124..127).contains(&t)));assert_eq!(y28_drop(t,rev),if chosen{3}else{baseline[2*t+usize::from(rev)]});}}}}
  std::env::remove_var("STACK_DROP130_RESEARCH");std::env::remove_var("STACK_DROP_EARLY_RESEARCH");
 }
}
''')
p=r/'run.py';s=p.read_text();needle=";assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build'";assert s.count(needle)==1;s=s.replace(needle,";assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','exact_early_drop_policy_tests','--','--nocapture','--test-threads=1'],'policy-tests')==0;assert 'test result: ok. 1 passed; 0 failed;'in(r/'policy-tests.log').read_text()"+needle)
ast.parse(s);p.write_text(s)
(r/'V2-SCOPE.md').write_text('''V1 eightnative controls andentirepublic3d7c controlPASS. Completecap1233-t21 Q1233/proxy755936.75; cap1232-t21 stops unchangedy16foldguard atforward127: foldshort23, pool16+tops2+fin4=22. No newpointcensus/nonce/score. V2 moves ONLY already-native-verified exactdrop3/50bit/7budget plan selector toforward127..136 forcap<=1232; old130..136 remainsforcap1233, reverse124..126 unchanged, allprimitiveguards remain. Addpolicytruth-table test preservingoriginal andnonselected ticks. No newone-foldtickrange/window/cut/nonce tuning.

Fixedresourcecases beforeinputs: public3d7c, previouspositivecap1233-t21 control,cap1232/1231-t21,cap1232/1231-u1,cap1232-u2. Witness21 exactlyparent. u1/u2 ONLY STRENGTHEN everycomparisonband by1/2 bits frompublic64:0,38:0,25:-3,0:-5 to64:1,38:1,25:-2,0:-4 or64:2,38:2,25:-1,0:-3. Allotherarithmetic/schedules unchanged. Selectresourcepromising sourcebeforefreshdevelopment andownfinalgate. No scoredresult fromstaticcounts; allfailures retained. Nativecomparator4/plan7+admission+phasefault4/newpolicy1 precedefullpubliccontrol andcompletegenerations.
''');print(r)
