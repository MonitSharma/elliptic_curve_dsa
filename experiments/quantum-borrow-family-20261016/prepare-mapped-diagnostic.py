from pathlib import Path
import hashlib,json
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016');source=r.parent/'failure-census-20261015/census/src/main.rs'
s=source.read_text()
reader='''
// Diagnostic only: preserve the exact original physical MR tape and inject
// zero for each independently phase-cancelled new cleanup outcome. The local
// theorem proves all q/phase results independent of these new outcomes.
struct MappedReader { original:sha3::Shake256Reader, extras:std::sync::Arc<Vec<usize>>, draws:std::rc::Rc<std::cell::Cell<usize>> }
impl XofReader for MappedReader {fn read(&mut self,out:&mut[u8]){assert_eq!(out.len(),8,"protected MR read shape changed");let i=self.draws.get();self.draws.set(i+1);if self.extras.binary_search(&i).is_ok(){out.fill(0);}else{XofReader::read(&mut self.original,out);}}}
'''
at=s.index('fn main()');s=s[:at]+reader+s[at:]
needle='    let regs = Arc::new(regs);';assert s.count(needle)==1
s=s.replace(needle,'    assert_eq!(ops.len(),11630908);assert_eq!(nq,1234);assert_eq!(nb,45702);let mut ordinal=0usize;let mut extra=Vec::new();for op in ops.iter(){if matches!(op.kind,OperationType::R|OperationType::Hmr){if op.kind==OperationType::Hmr&&op.c_target.0==45701{extra.push(ordinal);}ordinal+=1;}}assert_eq!(ordinal,906168);assert_eq!(extra.len(),12);let extras=Arc::new(extra);eprintln!("DIAGNOSTIC_MAPPED_OLD_MR_ONLY extra_outcomes0 justified_by_universal_phase_cleanup source=frozen_flag12 no_new_fresh_gate");\n'+needle)
needle='let (ops, regs, next, out, label) = (ops.clone(), regs.clone(), next.clone(), out.clone(), label.clone());';assert s.count(needle)==1
s=s.replace(needle,needle+'let extras=extras.clone();')
needle='                let mut sim = Simulator::new(nq as usize, nb as usize, &mut xof);';assert s.count(needle)==1
s=s.replace(needle,'                let draws=std::rc::Rc::new(std::cell::Cell::new(0));let mut mapped=MappedReader{original:xof,extras:extras.clone(),draws:draws.clone()};let mut sim = Simulator::new(nq as usize, nb as usize, &mut mapped);')
needle='                sim.apply_iter(ops.iter());';assert s.count(needle)==1
s=s.replace(needle,needle+'assert_eq!(draws.get(),906168);')
needle='let line = format!("{{\\\"batch\\\":{batch},';assert s.count(needle)==1
s=s.replace(needle,'let line = format!("{{\\\"diagnostic_mapped_original_mr\\\":true,\\\"batch\\\":{batch},')
tests='''
#[cfg(test)]mod mapped_tests{use super::*;
 #[test]fn injected_words_do_not_advance_original(){let mut h=Shake256::default();h.update(b"mapped-reader-test");let x=h.finalize_xof();let mut expected=x.clone();let draws=std::rc::Rc::new(std::cell::Cell::new(0));let mut m=MappedReader{original:x,extras:Arc::new(vec![0,2,7]),draws:draws.clone()};for i in 0..16{let mut actual=[0;8];XofReader::read(&mut m,&mut actual);if [0,2,7].contains(&i){assert_eq!(actual,[0;8]);}else{let mut want=[0;8];XofReader::read(&mut expected,&mut want);assert_eq!(actual,want);}}assert_eq!(draws.get(),16);}
 #[test]#[should_panic]fn changed_draw_shape_rejected(){let x=Shake256::default().finalize_xof();let mut m=MappedReader{original:x,extras:Arc::new(vec![]),draws:std::rc::Rc::new(std::cell::Cell::new(0))};XofReader::read(&mut m,&mut[0;16]);}
 #[test]fn inactive_hmr_still_consumes_both_draws(){use OperationType::*;let x=Shake256::default().finalize_xof();let d=std::rc::Rc::new(std::cell::Cell::new(0));let mut m=MappedReader{original:x,extras:Arc::new(vec![0]),draws:d.clone()};let mut o=Op::empty();o.kind=Hmr;o.q_target=QubitId(0);o.c_target=BitId(1);o.c_condition=BitId(0);let mut sim=Simulator::new(1,2,&mut m);sim.qubits[0]=u64::MAX;sim.apply(&o);sim.apply(&o);assert_eq!(sim.qubits[0],u64::MAX);assert_eq!(d.get(),2);}
}
'''
# Match the protected API name without assuming a single-op convenience method.
tests=tests.replace('sim.apply(&o);sim.apply(&o);','sim.apply_iter([&o,&o].into_iter());')
s+=tests
p=r/'proof-tool/src/bin/mapped_census.rs';p.write_text(s)
(r/'mapped-diagnostic-source.json').write_text(json.dumps(dict(status='DIAGNOSTIC ONLY; same frozen inputs and candidate; not another fresh gate',reference=str(source),reference_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),private_source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),changes='Private XofReader injects0 for12 certified phase-independent extra cleanup MR draws without advancing original stream; same protected Simulator, curve, loader and failure checks; everyphysicaldraw accounted.',new_cleanup_outcomes='0 selected only because the universal local theorem proves all final q/phase independent of them; not a circuit change'),indent=2)+'\n')
