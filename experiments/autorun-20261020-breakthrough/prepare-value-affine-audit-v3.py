from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'value-affine-audit.rs').read_text().replace('2_000_000','16_000_000')
needle='return vec![TV::unknown();p.nq];'
assert s.count(needle)==1
s=s.replace(needle,'return finish(p,i,q.iter().map(Poly::tv).collect(),c.iter().map(Poly::tv).collect());').replace('alloutputsUNKNOWN','sound_TV_continuation')
pos=s.index('#[cfg(test)]mod tests')
s=s[:pos]+'''fn finish(p:&Program,at:usize,mut q:Vec<TV>,mut c:Vec<TV>)->Vec<TV>{for n in &p.nodes[at..]{let g=p.guards[n.g as usize].iter().fold(TV::known(u64::MAX),|v,&x|v.and(c[x as usize]));let t=n.t as usize;match n.k{QX=>q[t]=q[t].xor(g),QCX=>q[t]=q[t].xor(g.and(q[n.a as usize])),QCCX=>q[t]=q[t].xor(g.and(q[n.a as usize]).and(q[n.b as usize])),QSWAP=>{let old=q[t];q[t]=g.ite(q[n.a as usize],old);q[n.a as usize]=g.ite(old,q[n.a as usize]);},QZERO=>q[t]=q[t].and(g.not()),CINV=>c[t]=c[n.a as usize].xor(g),CZERO=>c[t]=c[n.a as usize].and(g.not()),CONE=>c[t]=c[n.a as usize].or(g),CRNG=>c[t]=g.ite(TV::unknown(),c[n.a as usize]),_=>unreachable!()}}q}
''' +s[pos:]
pos=s.rfind('\n}')
s=s[:pos]+'''
 #[test]fn budget_fallback_is_the_same_sound_three_valued_machine(){use quantum_ecc::circuit::{Op,OperationType as K,QubitId,BitId};let mut x=Op::empty();x.kind=K::X;x.q_target=QubitId(0);x.c_condition=BitId(0);let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(1);h.c_target=BitId(1);let mut y=x;y.c_condition=BitId(1);let ops=vec![x,h,y];let p=super::super::compile(&ops,&[0]);let q=vec![0;p.nq];let bits=vec![0;p.nb];let expected=super::super::abstract_eval(&p,&q,&bits);let mut c=vec![TV::unknown();p.versions];for(i,&b)in bits.iter().enumerate(){c[i]=TV::known(b);}let actual=finish(&p,0,q.iter().map(|&v|TV::known(v)).collect(),c);for(a,b)in actual.iter().zip(expected){assert_eq!((a.z,a.o),(b.z,b.o));}}
''' +s[pos:]
(a/'value-affine-audit-v3.rs').write_text(s)
script=(a/'prepare-value-affine-audit.py').read_text().replace('breakthrough-value-affine-audit-20261020','breakthrough-value-affine-audit-v3-20261020').replace("a/'value-affine-audit.rs'","a/'value-affine-audit-v3.rs'").replace('native_controls=23','native_controls=24').replace(".replace('21 passed; 0 failed;','23 passed; 0 failed;')",".replace('21 passed; 0 failed;','24 passed; 0 failed;')").replace('2million','16million').replace('returns ALLUNKNOWN','continues with sound three-valued propagation').replace('return ALLUNKNOWN','continue with sound three-valued propagation').replace('(23total)','(24total incl fallback equivalence)')
ast.parse(script)
exec(compile(script,str(a/'prepare-value-affine-audit.py'),'exec'))
