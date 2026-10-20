from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-grouped-compact-width-v8-20261020';r=a.parent/'breakthrough-grouped-compact-width-v9-20261020';r.mkdir(exist_ok=False)
for p in old.iterdir():
 if p.is_file()and p.name not in ['SOURCE-FREEZE.json','RESULT.json','PROGRESS.json']:shutil.copyfile(p,r/p.name)
p=r/'prepare.py';s=p.read_text();needle="assert all(sha(t/p)==h for p,h in f['protected_files'].items());f['source_files']=";assert s.count(needle)==1
extra='''p=t/'src/point_add/fin1_fold_runtime.rs';raw=p.read_bytes();needle=b' super::super::super::phase_fit::cap()<1234&&cells::cap()<1234';assert raw.count(needle)==1;raw=raw.replace(needle,b' if super::super::super::phase_compare_compact::enabled()&&super::super::super::phase_fit::cap()==1234&&cells::cap()==1234{return true;}\\n'+needle);raw+=(r/'fin1-selector-tests.rs').read_bytes();p.write_bytes(raw)
''';s=s.replace(needle,extra+needle);ast.parse(s);p.write_text(s)
(r/'fin1-selector-tests.rs').write_text('''
#[cfg(test)]mod compact_fin1_selector_tests{
 use super::*;
 #[test]fn exact_equal_cap_fin1_route_preserves_all_shape_constraints(){
  for cap in [1233usize,1234,1235]{for enabled in [false,true]{std::env::set_var("PEBBLE_HARD_CAP",cap.to_string());std::env::set_var("EXACT_CMP_COMPACT",if enabled{"1"}else{"0"});for fin in [0,1,2]{for mw in [55,56,57]{for no_esh in [false,true]{for ttm in [false,true]{let got=super::super::super::super::pingpong::with_phase_cap(Some(cap),||selected(mw,fin,ttm,no_esh));let want=mw==56&&fin==1&&!ttm&&no_esh&&(cap<1234||(enabled&&cap==1234));assert_eq!(got,want);}}}}}}
  std::env::remove_var("EXACT_CMP_COMPACT");std::env::set_var("PEBBLE_HARD_CAP","1234");
 }
}
''')
p=r/'run.py';s=p.read_text();needle=";filters=['exact_strip_port_tests'";assert s.count(needle)==1;s=s.replace(needle,";assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','compact_fin1_selector_tests','--','--nocapture','--test-threads=1'],'fin1-selector-tests')==0;assert 'test result: ok. 1 passed; 0 failed;'in(r/'fin1-selector-tests.log').read_text();filters=['exact_strip_port_tests'");s=s.replace("'native_controls':33","'native_controls':34");ast.parse(s);p.write_text(s)
p=r/'phase-compare-compact.rs';s=p.read_text().replace('// The omitted allocated carry originally consumed BOTH an R and an HMR draw.','// Each omitted carry removes its HMR and its release-time R draw.');p.write_text(s)
(r/'V9-SCOPE.md').write_text('V8 fin0selector contract/nativecontrols/fulla871 controlPASS, thenlowercasesstop. Equalitycore_room30 choosesfin1 and its separate fin1_fold_runtime selector stilldisabledcap1234. V8 is ineligible estimate/runtime diagnostic; no gate/nonce/score. V9 enables matchingexactfin1 route onlywhen compactenabled andbothcaps1234, keeping old mw56/fin1/!ttm/no_esh constraints and oldsmaller-cap selectorverbatim. Fin0newcase unchanged. Addindependentfin1 admission truth-table test; bothselector tests, comparator4, prior27 includingfin1_fold_tests/core_loan_fold_tests/plan7_tests, group/square controls precedefulla871 control andlowercap cases. Existingcertificate/runtime algebra unchanged. Sourcefrozenbeforeinputs; no oldguard removed, no newprecision/window/cut. Documentationcorrection: R is emitted on free, notallocation; omittedcarryHMR plusreleaseR are correctlyreplaced by2kzeroHMRs. NumericalRNG tests alwayscheckedactualold/newdrawcounts. This scope supersedes historicalcopiedscopeprose. No scoredresult.\n')
(old/'INELIGIBLE-FIN1-SELECTOR-MISMATCH.md').write_text('Fin0 selector correction passes its native contract; the fin1 equality-cap route remains disabled and does not match the y16 estimate. This frozen prototype is ineligible diagnostics; no statistical gate/nonce/score. V9 adds the separate matching fin1 selector and native contract.\n');print(r)
