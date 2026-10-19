use super::*;
fn value(p:&P,n:u32)->bool{p.iter().fold(false,|v,m|v^m.iter().all(|id|n>>(id-1)&1!=0))}
#[test]fn thirteen_variable_sparse_products_match8192_scalar_assignments(){let mut g=Algebra{next:100,cap:256,degree:12,cuts:0};let a:P=(1..=12).map(|x|vec![x]).collect();let b=vec![vec![],vec![1,13],vec![2,3,11]];let x=g.xor(&a,&b);let y=g.and(&a,&b);for n in 0..8192{assert_eq!(value(&x,n),value(&a,n)^value(&b,n));assert_eq!(value(&y,n),value(&a,n)&value(&b,n));}assert_eq!(g.cuts,0);}
#[test]fn degree_fallback_replaces_whole_result_with_distinct_unknowns(){let mut g=Algebra{next:100,cap:256,degree:12,cuts:0};let a=vec![(1..=12).collect()];let b=vec![vec![13]];assert_eq!(g.and(&a,&b),vec![vec![100]]);assert_eq!(g.and(&a,&b),vec![vec![101]]);assert_eq!(g.cuts,2);}
