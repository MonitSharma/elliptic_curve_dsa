from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-grouped-compact-width-v7-20261020';r=a.parent/'breakthrough-grouped-compact-width-v8-20261020';r.mkdir(exist_ok=False)
for p in old.iterdir():
 if p.is_file() and p.name not in ['SOURCE-FREEZE.json','RESULT.json','PROGRESS.json']:shutil.copyfile(p,r/p.name)
p=r/'prepare.py';s=p.read_text();needle="assert all(sha(t/p)==h for p,h in f['protected_files'].items());f['source_files']=";assert s.count(needle)==1
extra='''p=t/'src/point_add/core_loan_runtime.rs';raw=p.read_bytes();needle=b' let global_route=super::super::super::phase_fit::cap()<1234&&cells::cap()<1234;';assert raw.count(needle)==1;extra=b' let exact_equal_route=super::super::super::phase_compare_compact::enabled()&&super::super::super::phase_fit::cap()==1234&&cells::cap()==1234;\\n if exact_equal_route{let room=cells::cap().saturating_sub(c.active_qubits()as usize)+usize::from(ttm);return room<=10;}\\n';raw=raw.replace(needle,extra+needle);raw+=(r/'core-selector-tests.rs').read_bytes();p.write_bytes(raw)
'''
s=s.replace(needle,extra+needle);ast.parse(s);p.write_text(s)
(r/'core-selector-tests.rs').write_text('''
#[cfg(test)]mod compact_core_selector_tests{
 use super::*;
 #[test]fn checked_equal_cap_route_matches_estimate_and_preserves_original_admission(){
  for cap in [1233usize,1234,1235]{for enabled in [false,true]{std::env::set_var("PEBBLE_HARD_CAP",cap.to_string());std::env::set_var("EXACT_CMP_COMPACT",if enabled{"1"}else{"0"});for room in 0..=12{let mut c=Builder::new();let q=c.alloc_qubits(cap-room);assert_eq!(c.active_qubits()as usize,cap-room);for fin in [0,1]{for mw in [55,56,57]{for no_esh in [false,true]{for ttm in [false,true]{for loan in [false,true]{let got=super::super::super::super::pingpong::with_phase_cap(Some(cap),||selected(&c,mw,fin,ttm,loan,no_esh));let want=fin==0&&no_esh&&mw==56&&(cap<1234||(enabled&&cap==1234))&&room+usize::from(ttm)<=10;assert_eq!(got,want,"cap{cap} enabled{enabled} room{room} fin{fin} mw{mw} no_esh{no_esh} ttm{ttm} loan{loan}");}}}}}drop(q);}}}
  std::env::remove_var("EXACT_CMP_COMPACT");std::env::set_var("PEBBLE_HARD_CAP","1234");
 }
}
''')
p=r/'run.py';s=p.read_text();needle=";filters=['exact_strip_port_tests'";assert s.count(needle)==1;s=s.replace(needle,";assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','compact_core_selector_tests','--','--nocapture','--test-threads=1'],'core-selector-tests')==0;assert 'test result: ok. 1 passed; 0 failed;'in(r/'core-selector-tests.log').read_text();filters=['exact_strip_port_tests'");s=s.replace("'native_controls':32","'native_controls':33");ast.parse(s);p.write_text(s)
(r/'V8-SCOPE.md').write_text('V7 identified a selector/runtime mismatch before any point-input sampling: y16 admission could choose newequalitycap1234 core_route while core_loan_runtime::selected stilldisabled allcap1234 routes. V7 is ineligible diagnostic construction regardlessofoutcome; no finalgate/nonce/score. V8 preserves original fin0/no_esh/mw56 guards and adds explicit bounded runtimecase onlywhen compactenabled andbothcaps==1234, originalroom<=10 includingttm adjustment. Originalsmaller-cap route/loanguard remainverbatimafternewcase. Addindependentselector truth-table test acrosscaps1233/1234/1235, allroom0..12, enabled/fin/mw/no_esh/ttm/loan conditions, checkcompatibilitywithestimate. Nativecomparator4/selector1/prior27/group/square tests repeat beforefulla871 control andlowcap1234/1233 generation. Exactphase/precision/window/predicate unchanged. No scoredresult/gate/nonce.\n')
(old/'INELIGIBLE-SELECTOR-MISMATCH.md').write_text('The new equality-cap admission estimate did not enable the matching runtime route. This prototype is preserved as an ineligible diagnostic construction, irrespective of generated resources. No statistical gate, nonce or scored result is permitted. V8 adds the explicit matching runtime case and an independent selector test before new inputs.\n');print(r)
