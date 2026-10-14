"""Independent exhaustive scalar checks of arbitrary-input control proofs."""
import importlib.util
import itertools
from pathlib import Path
import random
import unittest

spec=importlib.util.spec_from_file_location('values',Path(__file__).with_name('analyze-symbolic-controls.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
NO=m.NO

def op(kind,target=NO,bit=NO,condition=NO,c1=NO,c2=NO):
    return (kind,0,c2,c1,target,bit,condition,NO)

def check(program,term_cap=128,cache_cap=100_000):
    state=m.Values(range(3),range(2),term_cap,cache_cap)
    claims=[]
    for row in program:
        claims.append(state.identity(row));state.step(row)
    assert not state.stack
    draws=sum(row[0]==12 for row in program)
    for values in itertools.product((0,1),repeat=5+draws):
        q=dict(enumerate(values[:3]));bits=dict(enumerate(values[3:5]))
        outcomes=iter(values[5:]);base=1;stack=[]
        for row,claim in zip(program,claims):
            kind,_,c2,c1,target,bit,condition,_=row
            guard=base if condition==NO else base&bits.get(condition,0)
            if claim=='zero_guarded_product':
                controls=(target,)if kind==7 else(c1,)if kind==8 else(c1,target)if kind==9 else(c1,c2)if kind==13 else(c1,c2,target)
                product=guard
                for c in controls:product&=q.get(c,0)
                assert product==0,(row,claim,values)
            elif claim=='equal_quantum_controls':assert q.get(c1,0)==q.get(c2,0)
            elif claim=='constant_one_control':assert q.get(c1,0)==1 or q.get(c2,0)==1
            if kind==15:stack.append(base);base&=bits.get(condition,0)
            elif kind==16:base=stack.pop()
            elif kind in(6,8,13):
                value=guard
                if kind in(8,13):value&=q.get(c1,0)
                if kind==13:value&=q.get(c2,0)
                q[target]=q.get(target,0)^value
            elif kind==10 and guard:q[c1],q[target]=q.get(target,0),q.get(c1,0)
            elif kind in(11,12):
                draw=next(outcomes)if kind==12 else 0
                if guard:
                    q[target]=0
                    if kind==12:bits[bit]=draw
            elif kind==3:bits[bit]=bits.get(bit,0)^guard
            elif kind in(4,5)and guard:bits[bit]=int(kind==5)
    return claims

class Controls(unittest.TestCase):
    def test_equal_and_complement(self):
        p=[op(8,3,c1=0),op(13,4,c1=0,c2=3),op(6,3),op(13,4,c1=0,c2=3)]
        self.assertEqual(check(p)[1],'equal_quantum_controls')
        self.assertEqual(check(p)[3],'zero_guarded_product')
    def test_constant_one(self):
        p=[op(6,3),op(13,4,c1=0,c2=3)]
        self.assertEqual(check(p)[1],'constant_one_control')
    def test_stale_snapshot(self):
        p=[op(15,condition=0),op(3,bit=0),op(8,3,c1=0),op(12,3,bit=0),op(16),op(13,4,c1=0,c2=3)]
        check(p)
    def test_conditional_swap_reset(self):
        check([op(8,3,c1=0),op(10,3,c1=1,condition=0),op(12,3,bit=2,condition=1),op(13,4,c1=3,c2=1)])
    def test_random_programs_and_forgetting(self):
        rng=random.Random(4917603)
        for _ in range(400):
            p=[];depth=0;draws=0
            for _ in range(24):
                kind=rng.choice([3,4,5,6,7,8,9,10,11,12,13,14,15,16])
                if kind==16 and depth==0:kind=6
                if kind==15 and depth>=2:kind=6
                if kind==12 and draws>=3:kind=11
                if kind==15:depth+=1
                if kind==16:depth-=1
                draws+=kind==12
                target,c1,c2=rng.sample(range(5),3)
                p.append(op(kind,target,rng.randrange(4),rng.choice([NO,0,1,2,3]),c1,c2))
                if kind==15 and p[-1][6]==NO:p[-1]=op(kind,target,condition=0)
            p.extend(op(16)for _ in range(depth))
            check(p);check(p,term_cap=1,cache_cap=2)

if __name__=='__main__':unittest.main()
