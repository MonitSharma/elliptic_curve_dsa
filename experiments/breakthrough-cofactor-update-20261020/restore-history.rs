
/// Global inverse of the history eraser: recover address flags before queries.
pub(super) fn restore_history(c:&mut Builder,new_c:&[QubitId],new_d:&[QubitId],
    s0:QubitId,s1:QubitId,k1:QubitId,k2:QubitId){
    let(a,b,d)=(new_d[3],new_d[4],new_d[5]);c.x(a);c.x(b);c.ccx(a,b,k2);
    let u=c.alloc_qubit();c.ccx(b,d,u);c.x(u);c.ccx(a,u,k1);c.x(u);c.ccx(b,d,u);c.release_clean(u);c.x(b);c.x(a);
    query4(c,[new_d[4],new_d[5],new_d[6],new_d[7]],[k1,k2],s0);c.cx(new_c[1],s0);c.x(s0);
    query4(c,[new_d[5],new_d[6],new_d[7],new_d[8]],[k1,k2],s1);c.cx(new_c[2],s1);c.x(s1);
}
