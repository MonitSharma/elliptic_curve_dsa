"""Small exact ANF reference for carry-reader construction; no circuit input."""
import itertools,unittest
def xor(a,b):return a^b
def mul(a,b):
    out=set()
    for x in a:
        for y in b:
            term=x|y
            if term in out:out.remove(term)
            else:out.add(term)
    return out
def var(i):return {1<<i}
def decoded(compact=False):
    a,b,c=var(0),var(1),var(2);u=mul(a,c)
    return [a^c,c,c^b^u,b] if compact else [a^b^u,b^u,c^b^u,b]
def evaluate(p,assignment):return sum((assignment&m)==m for m in p)%2
def xor_cost(p):
    if any(m.bit_count()>2 for m in p):return None
    return sum(m.bit_count()==2 for m in p)
def phase_cost(p):
    if any(m.bit_count()>3 for m in p):return None
    return sum(m.bit_count()==3 for m in p)
class DecoderTests(unittest.TestCase):
    def test_every_body_value_for_all_basis_inputs(self):
        for compact in (False,True):
            p=decoded(compact)
            for a,b,c in itertools.product((0,1),repeat=3):
                carry=(a&b)^(a&c)^(b&c)
                encoded=(a^b)|(carry<<1)|((c^b)<<2)
                expected=[a^c,b^c,c,carry] if compact else [a,b,c,carry]
                self.assertEqual([evaluate(x,encoded) for x in p],expected)
    def test_all_products_and_guard_values(self):
        for compact in (False,True):
            p=decoded(compact)+[var(4),var(5)]
            for x,y in itertools.product(p,repeat=2):
                xy=mul(x,y)
                for bits in range(64):
                    for guard in (0,1):self.assertEqual(evaluate(xy,bits)&guard,evaluate(x,bits)&evaluate(y,bits)&guard)
    def test_compact_linear_queries_are_free(self):
        a,b,c,_=decoded(True)
        self.assertEqual([xor_cost(a),xor_cost(b),xor_cost(c)],[0,0,1])
        self.assertEqual(xor_cost(mul(a,var(4))),2)
        self.assertEqual(xor_cost(mul(b,var(4))),1)
    def test_full_internal_phase_pairs_are_free(self):
        a,b,c,_=decoded(False)
        self.assertEqual([phase_cost(mul(a,b)),phase_cost(mul(b,c)),phase_cost(mul(a,c))],[0,0,0])
    def test_unsupported_xor_degree_is_rejected(self):
        self.assertIsNone(xor_cost(mul(decoded(False)[0],var(4))))
        self.assertEqual(phase_cost(mul(decoded(False)[0],var(4))),1)
    def test_three_gate_cleanup_sum_and_restored_operands(self):
        for a,b,c in itertools.product((0,1),repeat=3):
            aa=a^b;cc=c^b;bb=b^(aa&cc)
            bb^=aa&cc;cc^=bb;aa^=cc
            self.assertEqual((aa,bb,cc),(a^b^c,b,c))
if __name__=='__main__':unittest.main()
