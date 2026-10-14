"""Bounded exact Boolean polynomial identities; conservative overflow abstraction."""
import argparse
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('symbolic',Path(__file__).with_name('analyze-symbolic-controls.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PolynomialValues(m.Values):
    def __init__(self,qubits=(),bits=(),term_cap=32,cache_cap=30_000):
        self.degree_cap=24
        super().__init__(qubits,bits,term_cap,cache_cap)

    def fresh(self):
        self.atom+=1
        return (0,frozenset((frozenset((self.atom,)),)))

    def and_(self,a,b):
        if a==m.ZERO or b==m.ZERO:return m.ZERO
        if a==m.ONE:return b
        if b==m.ONE or a==b:return a
        if a==self.inverse(b):return m.ZERO
        left=list(a[1])+([frozenset()]if a[0]else[])
        right=list(b[1])+([frozenset()]if b[0]else[])
        terms=set()
        for x in left:
            for y in right:
                term=x|y
                if len(term)>self.degree_cap:
                    self.forgotten+=1
                    return self.named(('polynomial_and_overflow',frozenset((a,b))))
                if term in terms:terms.remove(term)
                else:terms.add(term)
        if len(terms)>self.term_cap:
            self.forgotten+=1
            return self.named(('polynomial_and_overflow',frozenset((a,b))))
        constant=int(frozenset()in terms)
        terms.discard(frozenset())
        return (constant,frozenset(terms))

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('stream',type=Path);a.add_argument('output',type=Path)
    args=a.parse_args()
    m.Values=PolynomialValues
    d=m.analyze(args.stream)
    d['scope']='Exact bounded Boolean ANF arbitrary-input control identities; overflow replaces exact expressions by fresh unconstrained atoms. No transformed circuit or score.'
    d['degree_cap']=24
    args.output.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in d.items()if k!='ccx_examples'}))
