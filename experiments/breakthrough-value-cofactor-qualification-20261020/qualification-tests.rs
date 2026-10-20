
#[cfg(test)]mod above_bound_cofactor_tests{use super::*;
 fn masked(enable:bool)->(u32,u32){let mut e=Expr::default();e.restricting=!enable;let mut g=1;for _ in 0..6{let a=e.atom();g=e.and(g,a);}let mut old=1;for _ in 0..6{let a=e.atom();old=e.and(old,a);}assert_eq!(e.semantic(g).atoms.len(),6);assert_eq!(e.semantic(old).atoms.len(),6);let random=e.atom();let value=e.ite(g,random,old);let got=e.and(g,value);let expected=e.and(g,random);(got,expected)}
 #[test]fn masked_alias_above_six_atom_bound_requires_and_exercises_cofactor_rule(){let disabled=masked(false);assert_ne!(disabled.0,disabled.1,"negativecontrol must fail to canonicalize when exact cofactoring disabled");let enabled=masked(true);assert_eq!(enabled.0,enabled.1);}
}
