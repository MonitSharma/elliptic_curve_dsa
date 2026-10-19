"""Derive the paused variant from the source-bound passing plain component."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
p=r.parent/'breakthrough-parity-bridge-20261020/parity_bridge.rs'
raw=p.read_bytes();code=raw.split(b'#[cfg(test)]mod tests{')[0]
signature=b'pub(super) fn add(c:&mut Builder,acc:&[QubitId],terms:&[Vec<QubitId>],cin:Option<QubitId>,indices:&[usize])->bool{'
assert code.count(signature)==1
code=code.replace(signature,b'''pub(super) fn with_pause(c:&mut Builder,acc:&[QubitId],terms:&[Vec<QubitId>],cin:Option<QubitId>,indices:&[usize],protected_target:&[usize],protected_source:&[QubitId],mid:&mut dyn FnMut(&mut Builder,&[Option<QubitId>]))->bool{''')
needle=b'if i+2>=n||!chosen.insert(i)||i==0&&cin.is_none(){return false;}'
assert code.count(needle)==1
code=code.replace(needle,b'if i+2>=n||!chosen.insert(i)||i==0&&cin.is_none()||protected_target.contains(&i){return false;}')
needle=b'filter(|q|Some(*q)!=cin&&occurrences[&q.0]==1)';assert code.count(needle)==1
code=code.replace(needle,b'filter(|q|Some(*q)!=cin&&occurrences[&q.0]==1&&!protected_source.contains(q))')
old=b'''        if i+2==n{
            c.ccx(acc[i],v,acc[n-1]);off(c,&addend[i],ci);
            if let Some(q)=ci{c.cx(q,acc[n-1]);c.cx(q,acc[i]);}
        }else{
            let q=c.alloc_qubit();c.ccx(acc[i],v,q);off(c,&addend[i],ci);
            if let Some(ci)=ci{c.cx(ci,q);c.cx(ci,acc[i]);}carries[i+1]=Some(q);
        }'''
assert code.count(old)==1
code=code.replace(old,b'''        let q=c.alloc_qubit();c.ccx(acc[i],v,q);off(c,&addend[i],ci);
        if let Some(ci)=ci{c.cx(ci,q);c.cx(ci,acc[i]);}carries[i+1]=Some(q);''')
needle=b'    for i in(0..n).rev(){';assert code.count(needle)==2
code=code.replace(needle,b'''    // A borrowed MAJ changes its incoming carry wire. Expose only carries
    // whose following stage is ordinary, and the unchanged terminal carry.
    let mut exposed=carries.clone();
    for i in 0..n-1{if pivots[i].is_some(){exposed[i]=None;}}
    mid(c,&exposed);
    for i in(0..n).rev(){''',1)
header=b'''//! Paused mixed ladder. The callback may read original target bits only in
//! protected_target and original source bits only in protected_source. It
//! may use only Some carry views, and must restore all source/target/carry
//! values it touches. Outputs and phase work must use other wires. This
//! component is not yet integrated into the GCD callback machinery.
'''
code=header+code+(r/'tests.rs').read_bytes()
(r/'parity_paused.rs').write_bytes(code)
(r/'DERIVATION.json').write_text(json.dumps({'plain_source_sha256':hashlib.sha256(raw).hexdigest(),
    'paused_source_sha256':hashlib.sha256(code).hexdigest(),'scope':'Source-derived paused variant; admitted callback contract is part of correctness, not an inferred free-source claim.'},indent=2)+'\n')
