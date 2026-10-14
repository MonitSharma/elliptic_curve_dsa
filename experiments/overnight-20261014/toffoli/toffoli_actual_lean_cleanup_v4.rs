//! Narrow top1/direct/nondeep fin4/drop2 deferred lean cleanup; all input/phase identities frozen v3.
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

pub(super) fn run(c:&mut Builder,acc:&[QubitId],e:[QubitId;3],nm:[QubitId;3],shift:[QubitId;2],old_c3:QubitId,c6:QubitId,a4:&Lin,a5:&Lin,recs:Vec<Rec>) {
    assert_eq!(recs.len(),13,"source prefix after14 table erasures");
    let q=|i:usize|match &recs[i] {Rec::And(q,_,_)|Rec::Maj(q,_,_,_)=>*q,_=>panic!("carry marker")};
    let (old_tt,r1,r2,r3,y3,y4,y5,t3,t4,t5,sign)=(q(0),q(1),q(2),q(3),q(4),q(5),q(7),q(9),q(10),q(11),q(12));
    let live=[r1,r2,r3,y3,y4,y5,t3,t4,t5,sign,c6];
    let ids:std::collections::HashSet<u64>=live.iter().map(|q|q.0).collect();assert_eq!(ids.len(),11);
    for q in acc.iter().chain(e.iter()).chain(nm.iter()).chain(shift.iter()) {assert!(!ids.contains(&q.0));}
    assert!(!ids.contains(&old_c3.0));assert!(!ids.contains(&old_tt.0));
    let c1=lin_and(c,&l(acc[0]),&l(e[0]));
    let c2=maj_wire(c,&l(acc[1]),&l(e[1]),&l(c1));
    let tt=lin_and(c,&l(shift[0]),&l(shift[1]));
    let c4=lin_and(c,&l(acc[3]).x(&Lin::k(true)),&l(y3));
    let g=Lin::of(&[shift[0],shift[1],tt]);let one=Lin::k(true);
    // C5=AND(final4+a4,a4+C4)+C4, so one conditional AND repairs the C6 phase.
    let m6=c.alloc_bit();c.hmr(c6,m6);c.release_clean(c6);c.push_condition(m6);
    let pa=l(acc[4]).x(a4);let pb=a4.x(&l(c4));let p=lin_and(c,&pa,&pb);
    let l5=l(acc[5]).x(a5).x(&one);
    lin_cz(c,&l(p),&l5);lin_cz(c,&l(c4),&l5);
    lin_cz(c,a5,&l(acc[5]));lin_cz(c,&one,a5);
    lin_and_erase(c,p,&pa,&pb);c.pop_condition();c.free_bit(m6);
    let down=l(r3).x(&one);
    lin_and_erase(c,sign,&l(t5),&down);
    lin_and_erase(c,t5,&l(t4),&l(y5).x(&down));
    lin_and_erase(c,t4,&l(t3),&l(y4).x(&down));
    let m3=c.alloc_bit();c.hmr(t3,m3);c.push_condition(m3);
    lin_cz(c,&down,&l(y3));lin_cz(c,&g,&Lin::of(&[y3,c4]));
    c.pop_condition();c.free_bit(m3);c.release_clean(t3);
    lin_and_erase(c,y5,&l(tt),&l(acc[5]));
    lin_and_erase(c,y4,&l(shift[1]),&l(acc[4]));
    lin_and_erase(c,c4,&l(acc[3]).x(&one),&l(y3));
    let my=c.alloc_bit();c.hmr(y3,my);c.push_condition(my);
    lin_cz(c,&Lin::of(&[acc[2],c2]),&Lin::of(&[e[2],c2]));
    lin_cz(c,&one,&l(c2));lin_cz(c,&g,&l(acc[3]));
    c.pop_condition();c.free_bit(my);c.release_clean(y3);
    maj_wire_erase(c,r3,&l(nm[2]),&l(acc[2]),&l(r2));
    maj_wire_erase(c,r2,&l(nm[1]),&l(acc[1]),&l(r1));
    lin_and_erase(c,r1,&l(nm[0]),&l(acc[0]));
    lin_and_erase(c,tt,&l(shift[0]),&l(shift[1]));
    c.cx(e[2],acc[2]);c.cx(c2,acc[2]);
    maj_wire_erase(c,c2,&l(acc[1]),&l(e[1]),&l(c1));
    c.cx(e[1],acc[1]);c.cx(c1,acc[1]);
    lin_and_erase(c,c1,&l(acc[0]),&l(e[0]));c.cx(e[0],acc[0]);
}
