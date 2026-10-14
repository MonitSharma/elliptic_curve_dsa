"""Generate a source-bound all-measurement decision-diagram audit kernel."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
old=(HERE/'phase_polynomial.rs').read_text()
core=(HERE/'phase_decision_core.rs').read_text()
start=old.index('use std::collections::BTreeMap;')
end=old.index('#[derive(Debug)]\npub struct Audit')
text=old[:start]+core+'\n'+old[end:]
text='//! Exact decision-diagram phase audit of all measurements on fixed inputlanes.\n'+text[text.index('use crate::circuit'):]
text=text.replace('let m = Poly::variable(next_measurement);','let m = Poly::variable(next_measurement)?;')
text=text.replace('maximum_phase_terms','maximum_phase_size_bound').replace('maximum_quantum_terms','maximum_quantum_size_bound')
text=text.replace('let (nq, nb, _, _) = analyze_ops(ops.iter());','reset_manager();\n    let (nq, nb, _, _) = analyze_ops(ops.iter());',1)
text=text.replace('for (index, op) in ops.iter().enumerate() {','''for (index, op) in ops.iter().enumerate() {
        if index%32768==0 {GRAPH.with(|g|{let mut m=g.borrow_mut();if m.alive>400_000 || m.memo.len()>500_000 {let mut roots:Vec<u32>=q.iter().chain(&bits).chain(&stack).map(|p|p.0).collect();roots.extend([phase.0,base.0]);m.collect(&roots);}});}
''',1)
text=text.replace('phase.0.len()','phase.complexity()').replace('q[t].0.len()','q[t].complexity()').replace('q[a].0.len()','q[a].complexity()')
text=text.replace('if !phase.0.is_empty() {','if phase.scalar()!=Some(0) {')
text=text.replace('return Err(format!("nonzero phase polynomial: {} terms; first {:?}", phase.complexity(), phase.0.first_key_value()));','return Err(format!("nonzero phase polynomial represented by exact decision diagram: root={} size_bound={}",phase.0,phase.complexity()));')
begin=text.index('    #[test]\n    fn support_limit_is_inconclusive()')
text=text[:begin]+'''    #[test]
    fn node_budget_is_inconclusive_and_boolean_identities_hold(){
        reset_manager();let a=Poly::variable(0).unwrap();let b=Poly::variable(1).unwrap();
        let f=a.xor(&b).unwrap();assert_eq!(f.and(&f).unwrap(),f);
        assert_eq!(f.and(&f.not().unwrap()).unwrap().scalar(),Some(0));
        GRAPH.with(|g|g.borrow_mut().limit=g.borrow().nodes.len()+2);
        assert!(GRAPH.with(|g|{let mut m=g.borrow_mut();let _=m.branch(10,0,1)?;let _=m.branch(11,0,1)?;m.branch(12,0,1)}).unwrap_err().starts_with("inconclusive:"));
        reset_manager();
    }
}
'''
# Avoid nested RefCell borrows in the test budget setter.
text=text.replace('GRAPH.with(|g|g.borrow_mut().limit=g.borrow().nodes.len()+2);','GRAPH.with(|g|{let mut m=g.borrow_mut();m.limit=m.nodes.len()+2;});')
(HERE/'phase_decision_diagram.rs').write_text(text,encoding='utf-8',newline='\n')
runner=(HERE/'prepare-phase-polynomial-tests.py').read_text().replace('phase_polynomial.rs','phase_decision_diagram.rs').replace('phase_polynomial','phase_decision_diagram')
(HERE/'prepare-decision-phase-tests.py').write_text(runner,encoding='utf-8',newline='\n')
runner=(HERE/'prepare-qubit-phase-proof.py').read_text().replace('phase_polynomial.rs','phase_decision_diagram.rs').replace('maximum_phase_terms','maximum_phase_size_bound').replace('maximum_quantum_terms','maximum_quantum_size_bound')
runner=runner.replace('CONDITIONAL_PHASE_PROOF','DECISION_DIAGRAM_PHASE_PROOF')
(HERE/'prepare-qubit-decision-proof.py').write_text(runner,encoding='utf-8',newline='\n')
print(json.dumps({'kernel_sha256':hashlib.sha256((HERE/'phase_decision_diagram.rs').read_bytes()).hexdigest(),'scope':'Exact reduced ordered decision diagrams for all measurements on fixed inputlanes; fresh graph peraudit; node/depth limits areinconclusive'},indent=2))
