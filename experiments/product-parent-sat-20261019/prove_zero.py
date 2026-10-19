"""Universal SAT check on a source-bound interval; no sampled test inputs."""
import gzip,hashlib,json,struct,sys,time
from pathlib import Path
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r/'libraries'))
import z3
NO=(1<<64)-1
def prove(ops,depth=0,timeout=60000,save=None,seed=None,graph=None,first_index=0,zero_goal=False):
    context=z3.Context(proof=True)
    solver=z3.Solver(ctx=context);solver.set(timeout=timeout)
    q={};c={};linear_cache={}
    def boundary(e):
        k=tuple(e)
        if k not in linear_cache:
            value=z3.BoolVal(False,ctx=context)
            for atom in e:value=z3.Xor(value,z3.BoolVal(True,ctx=context) if atom==0 else z3.Bool(f'atom_{atom}',ctx=context))
            linear_cache[k]=z3.simplify(value)
        return linear_cache[k]
    stack=[boundary(e) for e in seed['stack']] if seed else [z3.BoolVal(True,ctx=context)]*depth
    guard=boundary(seed['base']) if seed else z3.BoolVal(True,ctx=context)
    def qb(w):
        assert w!=NO
        if w not in q:q[w]=boundary(seed['q'][str(w)]) if seed else z3.Bool(f'q{w}_input',ctx=context)
        return q[w]
    def cb(w):
        assert w!=NO
        if w not in c:c[w]=boundary(seed['c'][str(w)]) if seed else z3.Bool(f'c{w}_input',ctx=context)
        return c[w]
    def assign(table,w,expr,name):
        table[w]=expr
    initial=None
    for i,(kind,b,a,t,ct,cc,reg) in enumerate(ops):
        if i==first_index:
            initial=z3.And(qb(a),qb(b));solver.add(guard)
            if cc!=NO:solver.add(cb(cc))
        if i==len(ops)-1:
            assert kind==13
            solver.add(guard)
            if cc!=NO:solver.add(cb(cc))
            solver.add(z3.And(qb(a),qb(b)) if zero_goal else z3.Xor(initial,z3.And(qb(a),qb(b))))
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
    atoms=set();todo=list(solver.assertions());seen=set()
    while todo:
        e=todo.pop();ident=e.get_id()
        if ident in seen:continue
        seen.add(ident)
        if z3.is_const(e) and e.decl().kind()==z3.Z3_OP_UNINTERPRETED:
            name=str(e.decl().name())
            if name.startswith('atom_'):atoms.add(int(name[5:]))
        todo.extend(e.children())
    roots=sorted(atoms);expanded=set();iteration=0;start=time.monotonic()
    definitions=graph['definitions'] if graph else {}
    def relation(atom):
        kind,a,b=definitions[str(atom)]
        return boundary(a) if kind==0 else z3.And(boundary(a),boundary(b))
    while True:
        iteration+=1
        if graph:solver.set(timeout=min(30000,max(1,int(1000*(600-(time.monotonic()-start))))))
        verdict=solver.check()
        if verdict!=z3.sat or not graph or time.monotonic()-start>=600:break
        pending=[a for a in atoms if a not in expanded and str(a) in definitions]
        if not pending:break
        model=solver.model()
        def priority(atom):
            val=z3.Bool(f'atom_{atom}',ctx=context)
            mismatch=z3.is_true(model.eval(val,model_completion=True))!=z3.is_true(model.eval(relation(atom),model_completion=True))
            d=definitions[str(atom)]
            return (not mismatch,len(d[1])+len(d[2]),atom)
        batch=sorted(pending,key=priority)[:128]
        for atom in batch:
            solver.add(z3.Bool(f'atom_{atom}',ctx=context)==relation(atom));expanded.add(atom)
            _,aa,bb=definitions[str(atom)];atoms.update(x for x in aa+bb if x)
        if save:
            Path(str(save)+'.progress.json').write_text(json.dumps({'iteration':iteration,'expanded':len(expanded),'active_atoms':len(atoms),'seconds':time.monotonic()-start})+'\n')
    elapsed=time.monotonic()-start
    if save:
        with gzip.open(str(save)+'.smt2.gz','wt') as f:f.write(solver.to_smt2())
    result={'verdict':str(verdict),'seconds':elapsed,'quantum_boundary_variables':len(q),'classical_variables':len(c),'boundary_atoms':roots,'expanded_relations':len(expanded),'iterations':iteration,'missing_frontier_definitions':len([a for a in atoms if str(a) not in definitions]),'statistics':str(solver.statistics()),'reason_unknown':solver.reason_unknown() if verdict==z3.unknown else None}
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
    seed={'q':{str(i):[i+1] for i in range(4)},'c':{'0':[]},'base':[0],'stack':[]}
    assert prove(conditional,seed=seed)['verdict']=='unsat'
    seed['c']['0']=[5]
    assert prove(conditional,seed=seed)['verdict']=='sat'
    relation_ops=[ccx(0,1,4),ccx(2,3,1),ccx(0,1,5)]
    seed={'q':{str(i):[i+1] for i in range(6)},'c':{},'base':[0],'stack':[]}
    assert prove(relation_ops,seed=seed)['verdict']=='sat'
    graph={'definitions':{'3':[0,[0,1],[]]}}
    assert prove(relation_ops,seed=seed,graph=graph)['verdict']=='unsat'
    graph={'definitions':{'3':[0,[1],[]]}}
    assert prove(relation_ops,seed=seed,graph=graph)['verdict']=='sat'
    prelude=[[11,NO,NO,2,NO,NO,NO],[6,NO,NO,2,NO,NO,NO],[8,NO,0,2,NO,NO,NO]]
    body=[ccx(0,1,4),ccx(2,3,1),ccx(0,1,5)]
    assert prove(prelude+body,first_index=3)['verdict']=='unsat'
    bad=[prelude[0],prelude[2]]+body
    assert prove(bad,first_index=2)['verdict']=='sat'
    zero=[[11,NO,NO,0,NO,NO,NO],ccx(0,1,2)]
    assert prove(zero,first_index=1,zero_goal=True)['verdict']=='unsat'
    zero[0]=[6,NO,NO,0,NO,NO,NO]
    assert prove(zero,first_index=1,zero_goal=True)['verdict']=='sat'
    inactive=[[4,NO,NO,NO,0,NO,NO],[13,1,0,2,NO,0,NO]]
    assert prove(inactive,first_index=1,zero_goal=True)['verdict']=='unsat'
    print('14 SAT proof, zero-row and mutation tests passed',flush=True)
if __name__=='__main__':
    if sys.argv[1]=='test':tests();sys.exit(0)
    lookback=int(sys.argv[1]);prefix=f'zero-{lookback}';m=json.loads((r/(prefix+'.json')).read_text());raw=(r/m['raw_file']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==m['raw_sha256']
    ops=list(struct.iter_unpack('<7Q',raw));assert len(ops)==m['last']-m['start']+1
    seed=None;output=prefix
    mode='wide'
    if mode in ('seeded','roots','graph'):
        seed_path=r/f'boundary-{number:02}.json';seed=json.loads(seed_path.read_text())
        assert seed['base_pre_tail_sha3_256']==m['base_pre_tail_sha3_256']
        assert seed['first']==m['first'] and seed['last']==m['last']
        output=mode+'-'+prefix
    graph=None
    if mode=='graph':
        graph_path=r/f'relations-{number:02}.json';graph=json.loads(graph_path.read_text())
        assert graph['boundary_sha256']==hashlib.sha256(seed_path.read_bytes()).hexdigest()
        assert graph['base_pre_tail_sha3_256']==m['base_pre_tail_sha3_256']
    result=prove(ops,0,120000,r/output,first_index=m['first']-m['start'],zero_goal=True)
    result.update({'scope':'SOURCE_BOUND_UNIVERSAL_ZERO_EFFECT_PROOF','input':m,'z3_version':z3.get_version_string(),'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'status':'UNIVERSAL_ZERO_EFFECT_PASS' if result['verdict']=='unsat' else 'INCONCLUSIVE_LOCAL_BOUNDARY'})
    if seed:result['boundary_sha256']=hashlib.sha256(seed_path.read_bytes()).hexdigest()
    if graph:result['relations_sha256']=hashlib.sha256(graph_path.read_bytes()).hexdigest()
    (r/(output+'-result.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','verdict','seconds')}),flush=True)
