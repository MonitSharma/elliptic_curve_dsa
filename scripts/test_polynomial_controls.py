"""Exercise expanded Boolean identities with an independent scalar oracle."""
import importlib.util
from pathlib import Path
import unittest
import test_symbolic_controls as oracle

spec=importlib.util.spec_from_file_location('polynomial',Path(__file__).with_name('analyze-polynomial-controls.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
oracle.m.Values=p.PolynomialValues

class Expanded(oracle.Controls):
    def test_distributive_control_identity(self):
        s=p.PolynomialValues()
        a,b,c=s.fresh(),s.fresh(),s.fresh()
        self.assertEqual(s.and_(a,s.xor(b,c)),s.xor(s.and_(a,b),s.and_(a,c)))
        self.assertEqual(s.and_(s.xor(a,b),s.xor(a,b)),s.xor(a,b))
        self.assertEqual(s.xor(a,s.and_(a,b)),s.and_(a,s.inverse(b)))

if __name__=='__main__':unittest.main()
