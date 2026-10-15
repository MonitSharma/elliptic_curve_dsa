"""Independently replay saved Boolean equations and reject root negation faults.

This validates the solver equations, not their binding to an operation stream;
the separate source-bound cone exporter and native pairing establish that link.
"""
import argparse
import hashlib
import json
from pathlib import Path
import z3


def verify(path):
    data=json.loads(path.read_text()); results=[]
    for h in data['hits']:
        equations=h['equations']
        symbols={}
        def literal(i):
            if i<2: return z3.BoolVal(bool(i))
            k=i//2
            if k not in symbols: symbols[k]=z3.Bool('value_'+str(k))
            return z3.Not(symbols[k]) if i%2 else symbols[k]
        solver=z3.Solver();solver.set(timeout=30000)
        for identifier,kind,a,b in reversed(equations):
            rhs=(literal(a) & literal(b)) if kind=='and' else z3.Xor(literal(a),literal(b))
            solver.add(literal(identifier)==rhs)
        solver.push();solver.add(literal(h['root']));positive=str(solver.check());solver.pop()
        solver.push();solver.add(z3.Not(literal(h['root'])));negative=str(solver.check());solver.pop()
        assert positive=='unsat' and negative=='sat', (h['op'],positive,negative)
        # The true inverse statement must fail, showing the equations are consistent.
        results.append(dict(operation=h['op'],equations=len(equations),identity=positive,
                            negated_identity_fault=negative))
    return dict(status='saved_equations_verified_not_stream_binding',
                proof_file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                stream_sha256=data['stream_sha256'],solver=z3.get_version_string(),results=results)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('proofs',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=verify(a.proofs);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
