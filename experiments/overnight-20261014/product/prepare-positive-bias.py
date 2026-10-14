"""Uniform +2 square producer prototype; preserve old leaf through exact +4/-4 wrappers."""
from pathlib import Path
folder=Path(__file__).parent;out=folder/'positive-bias-source';out.mkdir(exist_ok=True)
source=folder/'source/point_add';s=source.joinpath('square.rs').read_bytes().decode()
start=s.index('fn tri_square_cin(');end=s.index('\nfn tri_square(',start);leaf=s[start:end]
needle='    assert!(m>=3);';assert leaf.count(needle)==1
leaf=leaf.replace(needle,needle+'\n    if inverse && row0_copy() {super::const_arith::sub_const(circ,product,U256::from(4));}')
needle='        diag_correction(circ,x,product,true);';assert leaf.count(needle)==1
leaf=leaf.replace(needle,needle+'\n        if row0_copy() {super::const_arith::add_const(circ,product,U256::from(4));}')
s=s[:start]+leaf+s[end:]
start=s.index('fn tri_square_k2r_inner(');end=s.index('\n/// Inverse of',start);node=s[start:end]
needle='    if row0_copy() {circ.x(b2[1]);}';assert node.count(needle)==2
at=node.rfind(needle);node=node[:at]+node[at:].replace(needle,'    // Uniform +2: keep b2 as unbiased b² through assembly.',1)
s=s[:start]+node+s[end:]
start=s.index('fn tri_square_k2r_inv(');end=s.index('\n/// Retained cross terms',start);inv=s[start:end]
assert inv.count('if row0_copy() {circ.x(b2[1]);}')==6
inv=inv.replace('if row0_copy() {circ.x(b2[1]);}','// b2 is already unbiased b²; restore +2 only before its inverse.')
needle='    square_b_inv(circ, bs, b2, high);';assert inv.count(needle)==1
inv=inv.replace(needle,'    if row0_copy() {circ.x(b2[1]);}\n'+needle)
s=s[:start]+inv+s[end:]
needle='    let acc=match super::optional_env::<usize>("SQ_ASM_TAIL"){Some(e)=>&full[..full.len().min(cross.len()+e)],None=>full};';assert s.count(needle)==1
s=s.replace(needle,'    let acc=full; // Exact full assembly for the +2 producer prototype.')
needle='fn k2r_offset(m: usize, flat: bool) -> U256 {';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    if row0_copy() {return U256::from(2);}')
s+='\n#[cfg(test)]\n#[path="tests_positive_bias.rs"]\nmod research_positive_bias;\n'
out.joinpath('square.rs').write_bytes(s.encode())
