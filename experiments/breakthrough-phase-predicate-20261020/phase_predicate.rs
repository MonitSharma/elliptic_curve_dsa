//! Exact carry-phase predicate with early measured carry erasure.
use super::builder::Builder;
use crate::circuit::QubitId;
use std::collections::BTreeSet;
fn on(c:&mut Builder,row:&[QubitId],one:bool,ci:QubitId)->QubitId{let q=if row.is_empty(){ci}else{let q=row[0];for &r in &row[1..]{c.cx(r,q);}c.cx(ci,q);q};if one{c.x(q);}q}
fn off(c:&mut Builder,row:&[QubitId],one:bool,ci:QubitId){let q=row.first().copied().unwrap_or(ci);if one{c.x(q);}if !row.is_empty(){c.cx(ci,q);for &r in row[1..].iter().rev(){c.cx(r,q);}}}
fn carry(c:&mut Builder,a:QubitId,row:&[QubitId],one:bool,ci:QubitId)->QubitId{c.cx(ci,a);let v=on(c,row,one,ci);let out=c.alloc_qubit();c.ccx(a,v,out);off(c,row,one,ci);c.cx(ci,out);c.cx(ci,a);out}
fn erase(c:&mut Builder,out:QubitId,a:QubitId,row:&[QubitId],one:bool,ci:QubitId){c.cx(ci,out);c.cx(ci,a);let v=on(c,row,one,ci);let bit=c.alloc_bit();c.hmr(out,bit);c.cz_if(a,v,bit);c.free_bit(bit);c.release_clean(out);off(c,row,one,ci);c.cx(ci,a);}
