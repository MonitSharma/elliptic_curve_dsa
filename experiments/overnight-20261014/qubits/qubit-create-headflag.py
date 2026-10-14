"""Aggregate disjoint SY cubes into the returned reciprocal flag.

The size-guarded small branch is unchanged. Test-only probes expose f at
each decision; production adds no wire or measurement operation.
"""
from pathlib import Path
import shutil,subprocess,sys
source,dest=map(lambda s:Path(s).resolve(),sys.argv[1:3])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for path in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert path.startswith('src/point_add/');shutil.copyfile(source/path,dest/path)
p=dest/'src/point_add/midg.rs';t=p.read_text();a=t.index('pub(crate) fn stage1_v_compact_partitioned(');z=t.index('// A V-form whose quotient reserve',a);part=t[a:z]
old='let selectors = size_partition(sy, small);';assert part.count(old)==1
part=part.replace(old,old+r'''
    #[cfg(test)]
    let hf_call = HF_PROBES.with(|bank| if bank.borrow().is_empty(){None}else{
        Some(HF_CALL.with(|call|{let value=call.get();call.set(value+1);value}))
    });
''')
old='b.x(s.f);\n        if !window { continue; }';assert part.count(old)==1
part=part.replace(old,r'''b.x(s.f);
        #[cfg(test)]
        if let Some(call)=hf_call {
            let probe=HF_PROBES.with(|bank|bank.borrow()[call*TC+j]);
            let fault=HF_FAULT_PROBE.with(|cell|cell.get()==Some(j));
            if fault{b.x(s.f);} b.cx(s.f,probe); if fault{b.x(s.f);}
        }
        if !window { continue; }''')
old='''} else if s.gt.len() == 1 {
            for selector in &selectors { let mut controls = [(act, false), (r[0], false)].to_vec(); controls.extend(selector.iter().copied()); inc_with_controls(b, &bits, &controls, &s.dirty); }
        } else {'''
new=r'''} else if s.gt.len() == 1 {
            // The odd comparator returns its c0 (r[0]) zero. The four
            // following toggles return f zero, including arbitrary inactive
            // remainder words. This driver's g0 is the same returned SX0.
            // SY is untouched by the window, so this predicate erases exactly.
            let predicate=rec(b,|b|for selector in &selectors{mc_xor(b,selector,g0,&[],&s.dirty);});
            b.play(&predicate,false);
            #[cfg(test)]
            if HF_FAULT_SELECTOR.with(|cell|cell.get()==Some(j)){b.x(g0);}
            inc_with_controls(b,&bits,&[(act,false),(r[0],false),(g0,false)],&s.dirty);
            #[cfg(test)]
            if HF_FAULT_SELECTOR.with(|cell|cell.get()==Some(j)){b.x(g0);}
            b.play(&predicate,true);
        } else {'''
assert part.count(old)==1;part=part.replace(old,new);t=t[:a]+part+t[z:]
t+=r'''

#[cfg(test)]
thread_local!{
    pub(crate) static HF_PROBES:std::cell::RefCell<Vec<QubitId>>=const{std::cell::RefCell::new(Vec::new())};
    pub(crate) static HF_CALL:std::cell::Cell<usize>=const{std::cell::Cell::new(0)};
    pub(crate) static HF_FAULT_PROBE:std::cell::Cell<Option<usize>>=const{std::cell::Cell::new(None)};
    pub(crate) static HF_FAULT_SELECTOR:std::cell::Cell<Option<usize>>=const{std::cell::Cell::new(None)};
}
''';p.write_text(t)
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text();a=t.index('#[test]\nfn n275_k32_k24_partition_all_sy_words');z=len(t);original=t[a:z]
# This function was the last appended primitive before the v2 full-column
# suite, so delimit at its next test rather than copying following functions.
if '#[test]'in original[10:]:original=original[:original.index('#[test]',10)]
audit=original.replace('n275_k32_k24_partition_all_sy_words','headflag_f_zero_each_iteration_active_inactive_dirty')
old='assert_eq!(b.width(),692);';assert old in audit
audit=audit.replace(old,r'''assert_eq!(b.width(),692);
    let probes=b.alloc_n(2*TC);let width=b.width()as usize;
    super::midg::HF_CALL.with(|cell|cell.set(0));
    super::midg::HF_PROBES.with(|bank|*bank.borrow_mut()=probes.clone());
    struct Clear;impl Drop for Clear{fn drop(&mut self){super::midg::HF_PROBES.with(|bank|bank.borrow_mut().clear());super::midg::HF_FAULT_PROBE.with(|cell|cell.set(None));super::midg::HF_FAULT_SELECTOR.with(|cell|cell.set(None));}}
    let _clear=Clear;''')
audit=audit.replace('(0..692)','(0..width)').replace('run(&forward,692','run(&forward,width').replace('run(&inverse,692','run(&inverse,width')
old='input[sx[0].0 as usize]=0;';assert old in audit;audit=audit.replace(old,old+'for &probe in &probes{input[probe.0 as usize]=0;}')
audit=audit.replace('K32_PARTITION_PASS','HEADFLAG_EACH_ITERATION_ZERO_PASS')
faults=r'''

#[test]
#[should_panic(expected="full SY partition")]
fn headflag_probe_self_fault_is_detected(){
    super::midg::HF_FAULT_PROBE.with(|cell|cell.set(Some(4)));
    headflag_f_zero_each_iteration_active_inactive_dirty();
}

#[test]
#[should_panic(expected="full SY partition")]
fn headflag_selector_self_fault_is_detected(){
    struct Clear;impl Drop for Clear{fn drop(&mut self){super::midg::HF_FAULT_SELECTOR.with(|cell|cell.set(None));}}
    let _clear=Clear;
    super::midg::HF_FAULT_SELECTOR.with(|cell|cell.set(Some(4)));
    n275_k32_k24_partition_all_sy_words();
}
'''
p.write_text(t+audit+faults)
