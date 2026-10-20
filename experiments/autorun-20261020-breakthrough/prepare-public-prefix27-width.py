from pathlib import Path
import ast,shutil

a=Path(__file__).parent;old=a.parent/'breakthrough-public-acd0-exact-width-v2-20261020';r=a.parent/'breakthrough-public-prefix27-width-20261020';r.mkdir(exist_ok=False)
for name in ['.gitattributes','.gitignore','additional-tests.rs','phase-compare-compact.rs','early-policy-tests.rs']:
 if (old/name).exists():shutil.copyfile(old/name,r/name)
s=(old/'prepare.py').read_text();needle="assert all(sha(t/p)==h for p,h in protected.items());prior=";assert s.count(needle)==1
extra=r"""
native=ws/'breakthrough-prefix27-fold-native-20261020';nf=json.loads((native/'SOURCE_FREEZE.json').read_text());assert(native/'run.exit').read_text().strip()=='0';assert all(sha(native/'primitive'/p)==h for p,h in {**nf['source_files'],**nf['protected_files']}.items())
for src,dest in [('prefix_schedule_runtime.rs','public_prefix27_runtime.rs'),('prefix_schedule_tests.rs','prefix_schedule_tests.rs'),('prefix_schedule_cleanup_tests.rs','prefix_schedule_cleanup_tests.rs'),('prefix_schedule_expected.dat','prefix_schedule_expected.dat')]:shutil.copyfile(native/'primitive/src/point_add'/src,t/'src/point_add'/dest)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def prefix_change(before,after):
 global raw
 assert raw.count(before)==1,(before,raw.count(before));raw=raw.replace(before,after)
prefix_change(b'at: (bool, usize), drop: usize) -> (usize, usize, usize, usize, usize)',b'at: (bool, usize), drop: usize, prefix_route: bool) -> (usize, usize, usize, usize, usize)')
prefix_change(b'let need = fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45);',b'let need = if prefix_route{28}else{fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45)};')
prefix_change(b'    (block, tops, c3m, gsh, fin)\n}',b'    (block, tops, c3m, gsh, if prefix_route{0}else{fin})\n}')
prefix_change(b'    let shed_for = |fixed: usize, fmax: usize| {',b'''    let nbits=fold_window(t,rev)-6;
    let least=(1..=nbits).find(|&b|merged_plan(nbits-1,b).is_some()||merged_plan(nbits,b).is_some()).expect("Exact original fold minimum");
    let ordinary_need=shed_fixed+least-drop_n-2*usize::from(Y15_LEAN45);
    let core_room=room_now+(N-4).saturating_sub(sp2)+tops_max;
    let prefix_route=public_prefix27_admit(super::super::phase_compare_compact::enabled(),cells::cap(),!rev&&!close&&!deep&&!swap01&&Y18_FIN_MIN==0&&fold_window(t,false)==56&&shed_on,core_room,fmax,ordinary_need);
    PUBLIC_PREFIX27_ROUTE.with(|v|v.set(prefix_route));
    let shed_for = |fixed: usize, fmax: usize| {''')
prefix_change(b'            drop_n,\n        )',b'            drop_n,\n            prefix_route,\n        )')
prefix_change(b'    let mw = acc.len();\n    let c1 = lin_and(c, &l(acc[0]), &l(e[0]));',b'''    let mw = acc.len();
    if PUBLIC_PREFIX27_ROUTE.with(|v|v.replace(false)){
        assert!(super::super::phase_compare_compact::enabled()&&cells::cap()<=1232&&mw==56&&fin==0&&esh.is_none(),"Exact prefix preflight/runtime selector mismatch");
        LOAN_ACTIVE.with(|v|v.set(false));let target=cells::cap();let(plan,peak)=c.r3_peak(|c|public_prefix27::full_fold(c,acc,e,nm,k1,k2,target));assert!(peak as usize<=target,"Complete exact prefix fold exceeds cap");eprintln!("PUBLIC_PREFIX27 target={target} peak={peak} plan={plan:?}");return plan;
    }
    let c1 = lin_and(c, &l(acc[0]), &l(e[0]));''')
raw+=b'\nthread_local!{static PUBLIC_PREFIX27_ROUTE:std::cell::Cell<bool>=const{std::cell::Cell::new(false)};}\nfn public_prefix27_admit(enabled:bool,cap:usize,shape:bool,room:usize,fmax:usize,need:usize)->bool{enabled&&cap<=1232&&shape&&room>=28&&room+fmax<need}\nmod public_prefix27{use super::*;include!("public_prefix27_runtime.rs");#[cfg(test)]include!("prefix_schedule_tests.rs");#[cfg(test)]include!("prefix_schedule_cleanup_tests.rs");}\n'
raw+=(r/'prefix-policy-tests.rs').read_bytes();p.write_bytes(raw)
"""
# The inserted code is itself Python source; only its byte-string newlines are escaped.
extra=extra.replace('\\\\n','\\n')
s=s.replace(needle,extra+'\n'+needle);ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text();needle="assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build')==0;rows=[]";assert s.count(needle)==1
s=s.replace(needle,"\n for flt,count in [('prefix_schedule_tests',2),('prefix_schedule_cleanup_tests',1),('prefix27_full_fold_tests',1),('public_prefix_policy_tests',1)]:\n  name='prefix-'+flt;assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',flt,'--','--nocapture','--test-threads=1'],name)==0;assert f'test result: ok. {count} passed; 0 failed;'in(r/(name+'.log')).read_text()\n assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build')==0;rows=[]")
ast.parse(s);(r/'run.py').write_text(s)
(r/'prefix-policy-tests.rs').write_text('''
#[cfg(test)]mod public_prefix_policy_tests{use super::*;
 #[test]fn new_route_only_replaces_insufficient_ordinary_fold_and_consumes_flag_once(){
  for enabled in[false,true]{for cap in[1231usize,1232,1233,1234]{for shape in[false,true]{for room in 0..=42{for fmax in 0..=6{for need in 28..=42{let got=public_prefix27_admit(enabled,cap,shape,room,fmax,need);let want=enabled&&cap<1233&&shape&&room>=28&&need>room+fmax;assert_eq!(got,want);if got{assert!(room>=28&&need>room+fmax);}}}}}}}
  PUBLIC_PREFIX27_ROUTE.with(|v|{v.set(true);assert!(v.replace(false));assert!(!v.replace(false));});
 }
}
''')
(r/'PLAN.md').write_text('''# Exact prefix scheduling port on current public product arithmetic

Port the independently verified27-helper prefix/20 retained functions/13-AND
cleanup/full56-bit forwardfold from the sealed native prototype. Keep original
public arithmetic/windows/witness21, generic passes and all capacity assertions.
The new route is admitted ONLY on compactcap<=1232, supported open forward56bit
shape, when the original fold cannot fit even with all existing sheds, and when
the exact prefix has at least28 helpers. A thread-local flag carries that exact
decision to the runtime, is consumed once, and asserts all runtime preconditions.
The full fold has its own measured peak assertion. No speculative budget change.

Native prefix2/cleanup1/fullfold1/policy1 plus original comparator4/plan4/policy1
must pass before complete construction. Full public control must remain exact
3d7c; cap1233 remains prior52a0 control. Fixed smaller-cap/strengthening grid is
unchanged. No point-input development, finalgate, nonce search or scored result.
Use fresh exact publicacd0 parent for any later product gate and auto-submit
only after qualifiednonce, unchanged benchmark and local evidence review.
''')
print(r)
