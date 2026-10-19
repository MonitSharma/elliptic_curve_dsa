import gzip,hashlib,json,sys
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;sys.path.insert(0,str(ws/'product-parent-sat-20261019/libraries'))
import z3
rows=json.loads((r/'AUDIT.json').read_text());assert len(rows)==3
results=[]
for i,row in enumerate(rows):
    variables={};cache={}
    def table(x):
        atoms=x['atoms'];bits=int(x['table_hex'],16);assert len(atoms)<=9 and bits>>(1<<len(atoms))==0
        key=(tuple(atoms),bits)
        if key in cache:return cache[key]
        terms=[]
        for assignment in range(1<<len(atoms)):
            if bits>>assignment&1:
                terms.append(z3.And(*[(variables.setdefault(a,z3.Bool('atom_'+str(a))) if assignment>>j&1 else z3.Not(variables.setdefault(a,z3.Bool('atom_'+str(a))))) for j,a in enumerate(atoms)]))
        v=z3.Or(*terms);cache[key]=v;return v
    base,direct,qa,qb,other,c=[table(row[k]) for k in ['base','direct','qa','qb','other','classical']]
    if row['negated']:c=z3.Not(c)
    s=z3.Solver();s.add(z3.Xor(z3.And(base,direct,qa,qb),z3.And(base,direct,other,c)))
    prefix=r/f'factor-{i:02}'
    with gzip.open(str(prefix)+'.smt2.gz','wt') as f:f.write(s.to_smt2())
    assert s.check()==z3.unsat
    replay=z3.Solver();replay.from_string(gzip.open(str(prefix)+'.smt2.gz','rt').read());assert replay.check()==z3.unsat
    results.append({'factor':i,'source_index':row['source_index'],'variables':len(variables),'verdict':'unsat','saved_smt2_replayed':True})
receipt=json.loads((r/'reproduced.json').read_text());assert receipt['output_full_sha3_256']=='2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265'
result={'status':'THREE_ADDITIONAL_SOURCE_BOUND_CLASSICAL_IDENTITIES_UNSAT_REPLAY_PASS','identities':results,'z3_version':z3.get_version_string(),'instrumented_output_identical':True,'scope':'Universal algebra extension after classical9. Not a new statistical gate, runtime acceptance, nonce result or scored resource benchmark.'}
(r/'PROOF.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
