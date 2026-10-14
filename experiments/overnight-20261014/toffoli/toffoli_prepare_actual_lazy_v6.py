"""Prepare narrowed producer-aware fin4 lazy helper with dirty class scratch."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[3];here=Path(__file__).parent
area=root/'research-output/overnight-20261014/toffoli'
base=(area/'actual-lean-v4-source/y15_onefold.rs').read_bytes()
assert hashlib.sha256(base).hexdigest()=='5da14bed2c72df4c2cb8005cec8feb0d381b5eb8adc73b2f5e2b6fa8aa3f2e59'
text=base.decode().replace('_v4','_v6')
text=text.replace('static TOFFOLI_ACTUAL_LEAN_C6:', 'static TOFFOLI_ACTUAL_LAZY_FREES:std::cell::RefCell<Vec<(usize,crate::circuit::BitId)>>=const{std::cell::RefCell::new(Vec::new())}; static TOFFOLI_ACTUAL_LAZY_TARGETS:std::cell::Cell<Option<[QubitId;4]>>=const{std::cell::Cell::new(None)}; static TOFFOLI_ACTUAL_LEAN_C6:')
needle='    TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.set(c.op_count()));'
assert text.count(needle)==1
text=text.replace(needle,needle+'''
    let tq=|i:usize|match &recs[i] {Rec::And(q,_,_)|Rec::Maj(q,_,_,_)=>*q,_=>panic!("prefix index")};
    TOFFOLI_ACTUAL_LAZY_TARGETS.with(|x|x.set(Some([c6,tq(9),tq(7),tq(4)])));''')
tests=(here/'toffoli_actual_lean_tests_v4.rs').read_text().replace('_v4','_v6')
tests=tests.replace('usize,u32);','[usize;4],u32,Vec<(usize,crate::circuit::BitId)>);')
tests=tests.replace('TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.set(0));', 'TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.set(0));TOFFOLI_ACTUAL_LAZY_FREES.with(|x|x.borrow_mut().clear());')
old='''    let c6=TOFFOLI_ACTUAL_LEAN_C6.with(|x|x.get()).unwrap();let boundary=TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.get());
    let final_esh=[esh.cq2,esh.cq1,esh.x258];let ops=c.take_ops();let mut mr=0usize;let mut c6_mr=None;
    for (i,op) in ops.iter().enumerate() {if matches!(op.kind,OperationType::Hmr|OperationType::R) {if i>=boundary && op.q_target==c6 && c6_mr.is_none() {c6_mr=Some(mr);}mr+=1;}}
    (ops,acc,controls,abi,pads,final_esh,c6_mr.unwrap(),peak)'''
new='''    let targets=TOFFOLI_ACTUAL_LAZY_TARGETS.with(|x|x.get()).unwrap();let boundary=TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.get());
    let final_esh=[esh.cq2,esh.cq1,esh.x258];let ops=c.take_ops();let mut mr=0usize;let mut indices=[None;4];
    for (i,op) in ops.iter().enumerate() {if matches!(op.kind,OperationType::Hmr|OperationType::R) {
        if i>=boundary {for j in 0..4 {if op.q_target==targets[j] && indices[j].is_none() {indices[j]=Some(mr);}}}mr+=1;
    }}
    let marks=TOFFOLI_ACTUAL_LAZY_FREES.with(|x|x.borrow().clone());assert_eq!(marks.is_empty(),!on);
    for &(cut,bit) in &marks {
        assert_eq!(ops[cut-1].kind,OperationType::BitStore0);assert_eq!(ops[cut-1].c_target,bit);assert_eq!(ops[cut-1].c_condition,crate::circuit::NO_BIT);
        let mut depth=0isize;for op in &ops[..cut] {if op.kind==OperationType::PushCondition {depth+=1;}if op.kind==OperationType::PopCondition {depth-=1;}}assert_eq!(depth,0,"zeroonfree outsideallconditions");
    }
    (ops,acc,controls,abi,pads,final_esh,indices.map(Option::unwrap),peak,marks)'''
assert tests.count(old)==1;tests=tests.replace(old,new)
tests=tests.replace('c6:usize,c6_word:u64','critical:[usize;4],pattern:u8').replace('let word=if self.index==self.c6 {self.c6_word}else{self.seed};','let word=if let Some(j)=self.critical.iter().position(|&i|i==self.index) {if self.pattern>>j&1!=0 {u64::MAX}else{0}}else{self.seed};')
tests=tests.replace('(ops,acc,controls,abi,pads,esh,c6_mr,peak)=fixture(on)', '(ops,acc,controls,abi,pads,esh,c6_mr,peak,marks)=fixture(on)')
tests=tests.replace('(mut ops,acc,controls,abi,pads,esh,_,_)=fixture(true)', '(mut ops,acc,controls,abi,pads,esh,_,_,_)=fixture(true)')
tests=tests.replace('(0..512).map(|i|0x93AB_CDEF_6789_4521u64.rotate_left((i%64) as u32))', '(0..nb as usize).map(|i|0x93AB_CDEF_6789_4521u64.rotate_left((i%64) as u32))')
tests=tests.replace('for c6_word in [0,u64::MAX,0xAAAA_AAAA_AAAA_AAAA]', 'for pattern in 0..16u8').replace('c6:c6_mr,c6_word','critical:c6_mr,pattern')
tests=tests.replace('sim.bits[..512].copy_from_slice(&bits);','sim.bits.copy_from_slice(&bits);')
tests=tests.replace('sim.apply_iter(ops.iter());','let mut cursor=0;for &(cut,bit) in &marks {sim.apply_iter(ops[cursor..cut].iter());assert_eq!(sim.bits[bit.0 as usize],0,"newclassscratchzeroonfree");cursor=cut;}sim.apply_iter(ops[cursor..].iter());')
tests=tests.replace('assert_eq!(&sim.bits[..512],&bits);', 'assert_eq!(&sim.bits[..512],&bits[..512]);')
tests=tests.replace('c6_mr={c6_mr}', 'critical_mr={c6_mr:?}').replace('freshESH={esh:?}', 'freshESH={esh:?} zero_free_checks={}',1)
tests=tests.replace('actualdrops=2 freshESH={esh:?} zero_free_checks={}");', 'actualdrops=2 freshESH={esh:?} zero_free_checks={}",marks.len());')
tests=tests.replace('assert_eq!(costs[0].0,costs[1].0+1);','assert_eq!(costs[0].0+1,costs[1].0);').replace('(costs[0].2/2) as u64','(7*costs[0].2/8) as u64').replace('total*3)', 'total*16)')
tests=tests.replace('TOFFOLI_ACTUAL_LEAN_V4', 'TOFFOLI_ACTUAL_LAZY_V6')
tests+='''
#[test]
fn toffoli_actual_lean_lazy_build_faults_v6() {
    let (ops,acc,controls,abi,pads,esh,_,_,_)=fixture(true);let boundary=TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.get());
    let ccx:Vec<_>=ops.iter().enumerate().skip(boundary).filter(|(_,op)|op.kind==OperationType::CCX).map(|(i,_)|i).collect();assert_eq!(ccx.len(),10,"threeESH,twoLowCarry,C4,factor,threeTT");
    for (name,remove) in [("C4_OR_build",ccx[5]),("TT_first_build",ccx[7])] {
        let mut faulty=ops.clone();faulty.remove(remove);let (nq,nb,_,_)=analyze_ops(faulty.iter());let bits:Vec<_>=(0..nb as usize).map(|i|0xA55A_F00F_93AC_4512u64.rotate_left((i%64) as u32)).collect();let mut detected=false;
        for base in (3<<16..4<<16).step_by(64) {let (input,_)=inputs(nq as usize,base,0,&acc,&controls,&abi,&pads,esh);
            if let Err(why)=super::toffoli_actual_lean_phase_kernel_v6::audit(&faulty,&input,&bits) {if why.starts_with("nonzero phase polynomial") {detected=true;break;}}
        }
        assert!(detected,"producer-admitted missing {name} phasefault");
    }
}
'''
out=area/'actual-lazy-v6-source';out.mkdir(parents=True,exist_ok=True)
(out/'y15_onefold.rs').write_bytes(text.encode());(out/'toffoli_actual_lean_tests_v6.rs').write_bytes(tests.encode())
(out/'toffoli_actual_lean_cleanup_v6.rs').write_bytes((here/'toffoli_actual_lean_cleanup_v6.rs').read_bytes().replace(b'\r\n',b'\n'))
kernel=(here.parent/'coordinator/phase-polynomial-v1.rs').read_bytes().replace(b'\r\n',b'\n');assert hashlib.sha256(kernel).hexdigest()=='330d91852ddc82740ac9bec4b8d8fb94d2ca5c5ca843fd4e56d1fed6123fab98'
(out/'toffoli_actual_lean_phase_kernel_v6.rs').write_bytes(kernel)
record={'status':'producer_aware_lazy_fin4_prepared_native_pending','source_sha256':{file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in out.iterdir()},
        'guard_truth_sha256':hashlib.sha256((here/'actual-lazy-guards-v5.json').read_bytes()).hexdigest(),'producer_contract_sha256':hashlib.sha256((here/'actual-esh-contract-v4.json').read_bytes()).hexdigest(),
        'scope':'Top1/direct/nondeep fin4/drop2, all18producer/fold inputs, fourhigherwords, actual2droppedchunks, ALL nb classicalbits initializeddirty, allnewownedflag-frees staticunconditionedSTORE0+nativezero checkpoints,512ABIunchanged.',
        'native_cost_scope':'All16 semanticC6/T3/Y5/Y3patterns equallyweighted foreachinput/layout; prospective−7/8mean,+1emittedCCX.',
        'actual_caller':'cap1234room37tick130,guard/allocation/cost only', 'qualified_score':None}
(here/'actual-lazy-v6-preparation.json').write_bytes((json.dumps(record,indent=2)+'\n').encode());print(json.dumps(record))
