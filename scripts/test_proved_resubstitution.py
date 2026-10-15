import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('search', Path(__file__).with_name('search-proved-resubstitution.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ProofTests(unittest.TestCase):
    def test_distributivity_and_wrong_witness(self):
        g = m.Cone()
        a, b, c = g.fresh(), g.fresh(), g.fresh()
        left = g.make('and', a, g.make('xor', b, c))
        right = g.make('xor', g.make('and', a, b), g.make('and', a, c))
        self.assertEqual(g.prove_zero(g.make('xor', left, right)[0])[0], 'unsat')
        self.assertEqual(g.prove_zero(g.make('xor', left, g.make('xor', right, c))[0])[0], 'sat')

    def test_forgotten_nodes_are_unconstrained(self):
        g = m.Cone(cap=3)
        a, b, c = g.fresh(), g.fresh(), g.fresh()
        old = g.make('and', a, b)
        for _ in range(5): g.make('and', g.fresh(), c)
        new = g.make('and', a, b)
        self.assertEqual(old[1], new[1])
        self.assertEqual(g.prove_zero(g.make('xor', old, new)[0])[0], 'sat')

    def test_guarded_identity_and_mutated_guard(self):
        g = m.Cone()
        a, b = g.fresh(), g.fresh()
        ab = g.make('and', a, b)
        diff = g.make('xor', ab, a)
        self.assertEqual(g.prove_zero(g.make('and', b, diff)[0])[0], 'unsat')
        self.assertEqual(g.prove_zero(g.make('and', g.neg(b), diff)[0])[0], 'sat')

    def test_resource_limit_is_not_proof(self):
        g = m.Cone()
        v = g.make('and', g.fresh(), g.fresh())
        self.assertEqual(g.prove_zero(v[0], max_nodes=1)[0], 'cone_limit')


if __name__ == '__main__': unittest.main()
