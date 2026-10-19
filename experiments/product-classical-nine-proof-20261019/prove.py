import gzip,hashlib,json,sys
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
sys.path.insert(0,str(ws/'product-parent-sat-20261019/libraries'))
import z3
rows=json.loads((r/'AUDIT.json').read_text());assert len(rows)==8
results=[]
for i,row in enumerate(rows):
    variables={};cache={}
    def table(x):
        atoms=x['atoms'];bits=int(x['table_hex'],16);assert len(atoms)<=7
        assert bits>>(1<<len(atoms))==0
        key=(tuple(atoms),bits)
        if key in cache:return cache[key]
        terms=[]
        for assignment in range(1<<len(atoms)):
            if bits>>assignment&1:
                terms.append(z3.And(*[(variables.setdefault(a,z3.Bool('atom_'+str(a))) if assignment>>j&1 else z3.Not(variables.setdefault(a,z3.Bool('atom_'+str(a))))) for j,a in enumerate(atoms)]))
        value=z3.Or(*terms);cache[key]=value;return value
    base,direct,qa,qb,other,classical=[table(row[k]) for k in ['base','direct','qa','qb','other','classical']]
    if row['negated']:classical=z3.Not(classical)
    s=z3.Solver();s.add(z3.Xor(z3.And(base,direct,qa,qb),z3.And(base,direct,other,classical)))
    prefix=r/f'factor-{i:02}'
    with gzip.open(str(prefix)+'.smt2.gz','wt') as f:f.write(s.to_smt2())
    assert s.check()==z3.unsat
    replay=z3.Solver();replay.from_string(gzip.open(str(prefix)+'.smt2.gz','rt').read());assert replay.check()==z3.unsat
    results.append({'factor':i,'source_index':row['source_index'],'variables':len(variables),'verdict':'unsat','saved_smt2_replayed':True})
# Universal XOR-of-live-classical-bits identity, including arbitrary dirty target.
u,v,y,t=z3.Bools('u v y t');s=z3.Solver()
s.add(z3.Xor(z3.Xor(t,z3.And(z3.Xor(u,v),y)),z3.Xor(z3.Xor(t,z3.And(u,y)),z3.And(v,y))))
assert s.check()==z3.unsat
with gzip.open(r/'ninth-xor.smt2.gz','wt') as f:f.write(s.to_smt2())
replay=z3.Solver();replay.from_string(gzip.open(r/'ninth-xor.smt2.gz','rt').read());assert replay.check()==z3.unsat
expected=json.loads((r/'reproduced.json').read_text());assert expected['output_full_sha3_256']=='f64a9d8c59cdc89e9b683988da84eb34fa78c5a884f0324ce824e4c07a00fa53'
expression=json.loads((ws/'product-classical-control-expression-20261019/EXPRESSION.json').read_text())
assert expression['input_full_sha3_256']==expected['output_full_sha3_256']
assert expression['expression_nodes']==[{'bit':773,'id':6532,'kind':'Live','negated':False},{'bit':774,'id':6535,'kind':'Live','negated':False},{'children':[6532,6535],'id':348052,'kind':'Xor','origin':None}]
assert expression['guard_proved_true'] and expression['captured_scope_depth']==0 and not expression['missing_variable_nodes']
receipt={'status':'EIGHT_SOURCE_BOUND_FACTOR_IDENTITIES_AND_NINTH_XOR_UNSAT_REPLAY_PASS','z3_version':z3.get_version_string(),'factors':results,'ninth_dirty_target_identity':'unsat; saved SMT2 replayed',
 'instrumented_output_identical':True,'instrumentation_sha256':hashlib.sha256((r/'INSTRUMENTATION.json').read_bytes()).hexdigest(),
 'exact_prefix_expression_sha256':hashlib.sha256((ws/'product-classical-control-expression-20261019/EXPRESSION.json').read_bytes()).hexdigest(),
 'scope':'Algebraic identities and exact prefix source certificate, not a failure gate, nonce filter acceptance or scored benchmark.'}
(r/'PROOF.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
