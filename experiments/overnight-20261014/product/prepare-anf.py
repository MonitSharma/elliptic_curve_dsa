"""Extend source-bound quadratic support to bounded exact Boolean ANF."""
from pathlib import Path
import sys
s=Path(sys.argv[1]);t=(s/'quadratic_simplify.rs').read_text()
t=t.replace('struct Quadratic','struct Polynomial').replace('Quadratic','Polynomial')
t=t.replace('atoms: Vec<(u64, u64)>','atoms: Vec<Vec<u64>>')
t=t.replace('#[derive(Clone, PartialEq, Eq)]','#[derive(Clone, Debug, PartialEq, Eq)]')
t=t.replace('atoms: vec![(id, id)]','atoms: vec![vec![id]]')
t=t.replace('atoms.push(a.atoms[i]);','atoms.push(a.atoms[i].clone());')
t=t.replace('atoms.push(b.atoms[j]);','atoms.push(b.atoms[j].clone());')
start=t.index('        let mut terms = BTreeSet::new();')
end=t.index('        if terms.len() > MONOMIAL_CAP {',start)
t=t[:start]+'''        let mut terms = BTreeSet::new();
        let toggle = |terms: &mut BTreeSet<Vec<u64>>, term: Vec<u64>| {
            if !terms.insert(term.clone()) { terms.remove(&term); }
        };
        if a.constant { for term in &b.atoms { toggle(&mut terms,term.clone()); } }
        if b.constant { for term in &a.atoms { toggle(&mut terms,term.clone()); } }
        for left in &a.atoms { for right in &b.atoms {
            // Boolean variables obey x*x=x. A monomial is its sorted support.
            let mut monomial=left.clone();monomial.extend(right);
            monomial.sort_unstable();monomial.dedup();
            if monomial.len()>DEGREE_CAP { return self.fresh(); }
            toggle(&mut terms,monomial);
        }}
'''+t[end:]
t=t.replace('const MONOMIAL_CAP: usize = 32;','const MONOMIAL_CAP: usize = 32;\nconst DEGREE_CAP: usize = 8;')
old='''                let rewrite = Self::ccx_rewrite(&condition, &a, &b, op);
                let product = self.and(&a, &b);
                let toggle = self.and(&condition, &product);'''
new='''                let product = self.and(&a, &b);
                let toggle = self.and(&condition, &product);
                let rewrite = if toggle.is_zero() { Rewrite::Drop }
                    else if toggle == condition { Rewrite::X }
                    else if toggle == self.and(&condition,&a) { Rewrite::Cx(op.q_control1) }
                    else if toggle == self.and(&condition,&b) { Rewrite::Cx(op.q_control2) }
                    else { Self::ccx_rewrite(&condition,&a,&b,op) };'''
assert t.count(old)==1;t=t.replace(old,new)
t=t.replace('//! Degree-two Boolean support identities, combined with the original affine pass.\n//! Monomials are canonical square-free pairs: (i,i) means atom i, (i,j)\n//! means their product. Atoms denote fixed functions, never mutable slots.\n//! An unsupported product or >32 monomials becomes one fresh whole-value atom.',
'''//! Exact Boolean algebra in square-free ANF, bounded to 32 terms/degree 8.
//! Atom IDs denote immutable Boolean functions, including measurements.
//! Unsupported whole operations get distinct fresh atoms; no term is dropped.
//! Snapshot conditions, all phase operations and measurement/reset ordering
//! match the inherited quadratic interpreter. These are universal identities
//! even when immutable Boolean atoms are correlated.''')
t+='\n#[cfg(test)]\n#[path="tests_bounded_anf.rs"]\nmod tests;\n'
(s/'bounded_anf.rs').write_text(t,newline='\n')
