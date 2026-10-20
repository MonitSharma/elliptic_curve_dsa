from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-exact-witness-ripple-v2-20261020';r=ex/'breakthrough-exact-witness-ripple-v3-20261020';r.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore','witness-tests.rs','sum-tests.rs','PLAN.md']:shutil.copyfile(old/n,r/n)
s=(old/'prepare.py').read_text()
for name in['EXACT_WITNESS_TEST_FAULT','EXACT_WITNESS_RIPPLE','EXACT_SQUARE_SHARED_SUM']:
 needle='super::env_flag("'+name+'")';assert needle in s;s=s.replace(needle,'std::env::var("'+name+'").is_ok_and(|v|v=="1")')
ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text().replace("('exact_witness_ripple_tests',3)","('exact_witness_ripple_tests',4)").replace("'native_components':4","'native_components':5");ast.parse(s);(r/'run.py').write_text(s)
p=r/'witness-tests.rs';s=p.read_text();pos=s.rfind('\n}');s=s[:pos]+'''\n #[test]fn deliberate_fault_then_clean_component_are_independent(){assert!(!exercise(259,3,true,true));assert!(exercise(259,3,true,false));}\n'''+s[pos:];p.write_text(s)
with(r/'PLAN.md').open('a')as out:out.write('''\nV2 native failure retained: inherited heo::passthrough caches process research\nswitch values in OnceLock<Mutex<HashMap>>. First deliberatefault test cached\nEXACT_WITNESS_TEST_FAULT=1; later set_var0 did not disarm fault. Originalreference\nchecks passed while newcomponent stayedfaulted. V3 reads ALL3newresearch switches\ndirectly via std::env, as existingGROUP_JUNCTION_FAULT did. Add4thnative regression\nthat runs deliberatefault then clean component in sameprocess; both outcomes\nmust be correct. Arithmetic/polynomial/full259 andfixedcases unchanged. No\npointinputs/census/gate/nonce rerun; allv1/v2source/logs preserved.\n''')
print(r)
