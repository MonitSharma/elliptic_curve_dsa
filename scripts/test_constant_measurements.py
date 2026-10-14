"""Condition-snapshot and arbitrary-ABI counterexamples for the read-only scan."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('scan',Path(__file__).with_name('analyze-constant-measurements.py'))
scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan)
NO=scan.NO
def op(kind,target=NO,bit=NO,condition=NO,c1=NO,c2=NO):return(kind,0,c2,c1,target,bit,condition,NO)
def result(program):return scan.analyze_rows(lambda:enumerate(program))

class Conditions(unittest.TestCase):
    def test_snapshot_survives_bit_mutation(self):
        program=[op(12,0,0),op(15,condition=0),op(3,bit=0),op(13,3,c1=1,c2=2),op(16),op(13,3,condition=0,c1=1,c2=2)]
        d=result(program);self.assertEqual([x['index']for x in d['guarded_operations']],[3])
    def test_arbitrary_abi_is_never_assumed_zero(self):
        d=result([op(12,0,0),op(13,3,condition=0,c1=1,c2=2),op(2,0)])
        self.assertEqual(d['constant_unconditional_hmr'],0)
    def test_conditional_measurement_not_admitted(self):
        d=result([op(2,bit=4),op(12,0,0,condition=4),op(13,3,condition=0,c1=1,c2=2)])
        self.assertEqual(d['constant_unconditional_hmr'],0)
    def test_multiple_positive_guards_count_once(self):
        d=result([op(12,0,0),op(12,1,1),op(15,condition=0),op(13,3,condition=1,c1=4,c2=5),op(16)])
        self.assertEqual(d['distinct_positive_guarded_toffolis'],1)
        self.assertEqual(len(d['guarded_operations'][0]['constant_measurements']),2)
    def test_constant_one_and_reused_measurement_bit(self):
        d=result([op(6,0),op(12,0,0),op(13,3,condition=0,c1=1,c2=2),op(12,4,0),op(13,3,condition=0,c1=1,c2=2)])
        self.assertEqual([x['constant']for x in d['useful_sites']],[1,0])
        self.assertEqual([x['positive_guarded_toffolis']for x in d['useful_sites']],[1,1])

if __name__=='__main__':unittest.main()
