//! Narrow top1/direct/nondeep fin3/drop1 deferred lean cleanup; all input/phase identities frozen v3.
use super::*;
pub(super) fn erase_tables(c:&mut Builder,old_c3:QubitId,mut recs:Vec<Rec>)->Vec<Rec> {
    assert_eq!(recs.len(),27);
    let q=|i:usize|match &recs[i] {Rec::And(q,_,_)|Rec::Maj(q,_,_,_)=>*q,_=>panic!("carry marker")};
    let old_tt=q(0);let y3=q(4);
    // k3=y3loan+r3. Every table operand loses its old c3 read; no original E or low carry is read.
    for _ in 0..14 {
        let Rec::And(q,mut a,mut b)=recs.pop().unwrap() else {panic!("table is plain AND records")};
        for form in [&mut a,&mut b] {
            if form.w.contains(&y3) {*form=form.x(&l(old_c3));}
            assert!(!form.w.contains(&old_c3));assert!(!form.w.contains(&old_tt));
        }
        lin_and_erase(c,q,&a,&b);
    }
    assert_eq!(recs.len(),13);
    recs
}

fn late_tt(c:&mut Builder,q:QubitId,k:[QubitId;2],need:crate::circuit::BitId,measured:crate::circuit::BitId) {
    let missing=c.alloc_bit();c.bit_store1(missing);c.bit_xor_into(missing,need);
    c.push_condition(measured);c.push_condition(missing);
    lin_and_into(c,q,&l(k[0]),&l(k[1]));c.bit_store1(need);
    c.pop_condition();c.pop_condition();c.bit_store0(missing);c.free_bit(missing);
}
fn erase_guarded(c:&mut Builder,q:QubitId,a:&Lin,b:&Lin,guard:crate::circuit::BitId) {
    // q is exactlyzero outsideguard, so unconditionalHMR is phase-neutral there.
    let m=c.alloc_bit();c.hmr(q,m);c.push_condition(guard);c.push_condition(m);lin_cz(c,a,b);
    c.pop_condition();c.pop_condition();c.bit_store0(m);c.free_bit(m);c.release_clean(q);
}
pub(super) fn run(c:&mut Builder,acc:&[QubitId],e:[QubitId;3],nm:[QubitId;3],shift:[QubitId;2],old_c3:QubitId,c6:QubitId,a4:&Lin,a5:&Lin,recs:Vec<Rec>) {
    assert_eq!(recs.len(),13);
    let q=|i:usize|match &recs[i] {Rec::And(q,_,_)|Rec::Maj(q,_,_,_)=>*q,_=>panic!("carry marker")};
    let (old_tt,r1,r2,r3,y3,y4,y5,t3,t4,t5,sign)=(q(0),q(1),q(2),q(3),q(4),q(5),q(7),q(9),q(10),q(11),q(12));
    let live=[r1,r2,r3,y3,y4,y5,t3,t4,t5,sign,c6];let ids:std::collections::HashSet<u64>=live.iter().map(|q|q.0).collect();assert_eq!(ids.len(),11);
    for q in acc.iter().chain(e.iter()).chain(nm.iter()).chain(shift.iter()) {assert!(!ids.contains(&q.0));}
    assert!(!ids.contains(&old_c3.0));assert!(!ids.contains(&old_tt.0));
    let c1=lin_and(c,&l(acc[0]),&l(e[0]));let c2=maj_wire(c,&l(acc[1]),&l(e[1]),&l(c1));
    let tt=c.alloc_qubit();let c4=c.alloc_qubit();let need_tt=c.alloc_bit();c.bit_store0(need_tt);
    let g=Lin::of(&[shift[0],shift[1],tt]);let one=Lin::k(true);let down=l(r3).x(&one);
    let m6=c.alloc_bit();c.hmr(c6,m6);c.release_clean(c6);
    // These erasures do not readC6 or mutateits correction operands.
    lin_and_erase(c,sign,&l(t5),&down);lin_and_erase(c,t5,&l(t4),&l(y5).x(&down));lin_and_erase(c,t4,&l(t3),&l(y4).x(&down));
    let m3=c.alloc_bit();c.hmr(t3,m3);c.release_clean(t3);
    let need4=c.alloc_bit();c.bit_store0(need4);
    for m in [m6,m3] {c.push_condition(m);c.bit_store1(need4);c.pop_condition();}
    let c4a=l(acc[3]).x(&one);let c4b=l(y3);c.push_condition(need4);lin_and_into(c,c4,&c4a,&c4b);c.pop_condition();
    let pa=l(acc[4]).x(a4);let pb=a4.x(&l(c4));let p=c.alloc_qubit();let l5=l(acc[5]).x(a5).x(&one);
    c.push_condition(m6);lin_and_into(c,p,&pa,&pb);lin_cz(c,&l(p),&l5);lin_cz(c,&l(c4),&l5);lin_cz(c,a5,&l(acc[5]));lin_cz(c,&one,a5);c.pop_condition();
    erase_guarded(c,p,&pa,&pb,m6);
    late_tt(c,tt,shift,need_tt,m3);c.push_condition(m3);lin_cz(c,&down,&l(y3));lin_cz(c,&g,&Lin::of(&[y3,c4]));c.pop_condition();
    c.bit_store0(m6);c.free_bit(m6);c.bit_store0(m3);c.free_bit(m3);
    erase_guarded(c,c4,&c4a,&c4b,need4);c.bit_store0(need4);c.free_bit(need4);
    let m5=c.alloc_bit();c.hmr(y5,m5);c.release_clean(y5);late_tt(c,tt,shift,need_tt,m5);
    c.push_condition(m5);lin_cz(c,&l(tt),&l(acc[5]));c.pop_condition();c.bit_store0(m5);c.free_bit(m5);
    lin_and_erase(c,y4,&l(shift[1]),&l(acc[4]));
    let my=c.alloc_bit();c.hmr(y3,my);c.release_clean(y3);late_tt(c,tt,shift,need_tt,my);
    c.push_condition(my);lin_cz(c,&Lin::of(&[acc[2],c2]),&Lin::of(&[e[2],c2]));lin_cz(c,&one,&l(c2));lin_cz(c,&g,&l(acc[3]));c.pop_condition();c.bit_store0(my);c.free_bit(my);
    maj_wire_erase(c,r3,&l(nm[2]),&l(acc[2]),&l(r2));maj_wire_erase(c,r2,&l(nm[1]),&l(acc[1]),&l(r1));lin_and_erase(c,r1,&l(nm[0]),&l(acc[0]));
    erase_guarded(c,tt,&l(shift[0]),&l(shift[1]),need_tt);c.bit_store0(need_tt);c.free_bit(need_tt);
    c.cx(e[2],acc[2]);c.cx(c2,acc[2]);maj_wire_erase(c,c2,&l(acc[1]),&l(e[1]),&l(c1));
    c.cx(e[1],acc[1]);c.cx(c1,acc[1]);lin_and_erase(c,c1,&l(acc[0]),&l(e[0]));c.cx(e[0],acc[0]);
}
