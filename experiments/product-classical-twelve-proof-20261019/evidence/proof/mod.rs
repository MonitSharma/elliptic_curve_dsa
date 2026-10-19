mod affine_simplify;
mod quadratic_simplify;
#[path="wide/mod.rs"] mod classical_factors_xor;
pub fn run(v:Vec<crate::circuit::Op>)->Vec<crate::circuit::Op>{classical_factors_xor::simplify_classical(v)}
