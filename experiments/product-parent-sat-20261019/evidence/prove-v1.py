"""Universal SAT check on a source-bound interval; no sampled test inputs."""
import gzip,hashlib,json,struct,sys,time
from pathlib import Path
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r/'libraries'))
import z3
NO=(1<<64)-1
def prove(ops,depth=0,timeout=60000,save=None):
    context=z3.Context(proof=True)
    solver=z3.Solver(ctx=context);solver.set(timeout=timeout)
    q={};c={};stack=[z3.BoolVal(True,ctx=context)]*depth;guard=z3.BoolVal(True,ctx=context)
    def qb(w):
        assert w!=NO
        if w not in q:q[w]=z3.Bool(f'q{w}_input',ctx=context)
        return q[w]
    def cb(w):
        assert w!=NO
        if w not in c:c[w]=z3.Bool(f'c{w}_input',ctx=context)
        return c[w]
    def assign(table,w,expr,name):
        lit=z3.Bool(name,ctx=context);solver.add(lit==expr);table[w]=lit
    initial=None
    for i,(kind,b,a,t,ct,cc,reg) in enumerate(ops):
        if i==0:initial=z3.And(qb(a),qb(b))
        if i==len(ops)-1:
            assert kind==13
            solver.add(guard)
            if cc!=NO:solver.add(cb(cc))
            solver.add(z3.Xor(initial,z3.And(qb(a),qb(b))))
            break
        if kind==15:stack.append(guard);guard=z3.And(guard,cb(cc));continue
        if kind==16:guard=stack.pop();continue
        eff=guard if cc==NO else z3.And(guard,cb(cc))
        if kind==6:assign(q,t,z3.Xor(qb(t),eff),f'q{t}_at{i}')
        elif kind==8:assign(q,t,z3.Xor(qb(t),z3.And(eff,qb(a))),f'q{t}_at{i}')
        elif kind==13:assign(q,t,z3.Xor(qb(t),z3.And(eff,qb(a),qb(b))),f'q{t}_at{i}')
        elif kind==10:
            old_a,old_t=qb(a),qb(t)
            assign(q,a,z3.If(eff,old_t,old_a),f'q{a}_at{i}')
            assign(q,t,z3.If(eff,old_a,old_t),f'q{t}_at{i}')
        elif kind in (11,12):
            assign(q,t,z3.And(qb(t),z3.Not(eff)),f'q{t}_at{i}')
            if kind==12:assign(c,ct,z3.If(eff,z3.Bool(f'm_at{i}',ctx=context),cb(ct)),f'c{ct}_at{i}')
        elif kind==3:assign(c,ct,z3.Xor(cb(ct),eff),f'c{ct}_at{i}')
        elif kind==4:assign(c,ct,z3.And(cb(ct),z3.Not(eff)),f'c{ct}_at{i}')
        elif kind==5:assign(c,ct,z3.Or(cb(ct),eff),f'c{ct}_at{i}')
        elif kind in (0,1,2,7,9,14,17):pass
        else:raise RuntimeError(kind)
    if save:
        with gzip.open(str(save)+'.smt2.gz','wt') as f:f.write(solver.to_smt2())
    start=time.monotonic();verdict=solver.check();elapsed=time.monotonic()-start
    result={'verdict':str(verdict),'seconds':elapsed,'quantum_boundary_variables':len(q),'classical_variables':len(c),'statistics':str(solver.statistics()),'reason_unknown':solver.reason_unknown() if verdict==z3.unknown else None}
    if save and verdict==z3.unsat:
        with gzip.open(str(save)+'.proof.gz','wt') as f:f.write(str(solver.proof()))
    if save and verdict==z3.sat:
        with gzip.open(str(save)+'.model.gz','wt') as f:f.write(str(solver.model()))
    return result
def tests():
    ccx=lambda a,b,t:[13,b,a,t,NO,NO,NO]
    good=[ccx(0,1,2),[8,NO,0,1,NO,NO,NO],[6,NO,NO,1,NO,NO,NO],ccx(0,1,3)]
    assert prove(good)['verdict']=='unsat'
    assert prove([good[0],good[1],good[3]])['verdict']=='sat'
    conditional=[ccx(0,1,2),[6,NO,NO,1,NO,0,NO],ccx(0,1,3)]
    assert prove(conditional)['verdict']=='sat'
    # A third-control conditional complement preserves the product; this is
    # beyond the old opaque symmetric-product matcher but follows Boolean laws.
    more=[ccx(0,1,3),[6,NO,NO,0,NO,NO,NO],ccx(0,2,1),[6,NO,NO,0,NO,NO,NO],ccx(0,1,4)]
    assert prove(more)['verdict']=='unsat'
    print('4 SAT proof and mutation tests passed',flush=True)
if __name__=='__main__':
    if sys.argv[1]=='test':tests();sys.exit(0)
    number=int(sys.argv[1]);prefix=f'lease-{number:02}';m=json.loads((r/(prefix+'.json')).read_text());raw=(r/m['raw_file']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==m['raw_sha256']
    ops=list(struct.iter_unpack('<7Q',raw));assert len(ops)==m['last']-m['first']+1
    result=prove(ops,m['initial_depth'],120000,r/prefix)
    result.update({'scope':'ARBITRARY_BOUNDARY_VALUE_PROOF_NOT_A_CENSUS','input':m,'z3_version':z3.get_version_string(),'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'status':'UNIVERSAL_PRODUCT_EQUALITY_PASS' if result['verdict']=='unsat' else 'INCONCLUSIVE_LOCAL_BOUNDARY'})
    (r/(prefix+'-result.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','verdict','seconds')}),flush=True)
