"""Cross-check the independent model against preserved source-model failures."""
import collections
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('screen',Path(__file__).with_name('screen-qubit-capacity.py'))
MODEL=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODEL)

class CapacityRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=[list(map(int,l.split()[1:]))for l in (ROOT/'agents/qubits/src/point_add/sched_frogdrop.txt').read_text().splitlines()if l.startswith('C ')]
        cls.inputs={}
        for line in (ROOT/'research-output/overnight-20261014/qubits/compact-packet.tsv').read_text().splitlines():
            w=line.split()
            if not w or w[0].startswith('#'):continue
            if int(w[0]) not in [1170,1937,3713,4131,4202,8048]:continue
            for d,i in [(1,1),(2,5)]:cls.inputs[int(w[0]),d]=(int(w[i],16)-int(w[3],16))%MODEL.P

    def old(self,dx):
        return MODEL.screen(dx,self.rows,collections.Counter(),small_head=24,mixed_cap=23,pure_cap=23,reserve=7)

    def test_matches_six_public_source_model_failures(self):
        observed={key:events[0]['kind']for key,dx in self.inputs.items()if(events:=self.old(dx))}
        self.assertEqual(observed,{(1170,2):'reciprocal_HR',(1937,2):'reciprocal_HR',(3713,1):'parking',(4131,1):'reciprocal_HT',(4202,2):'reciprocal_HR',(8048,2):'reciprocal_HR'})

    def test_proposal_clears_same_twelve_divisions(self):
        for key,dx in self.inputs.items():
            with self.subTest(input=key):self.assertEqual(MODEL.screen(dx,self.rows,collections.Counter()),[])

    def test_reserve_eight_preserves_crossing_counterexample(self):
        events=MODEL.screen(self.inputs[3713,1],self.rows,collections.Counter(),reserve=8)
        self.assertEqual([(e['kind'],e.get('required'))for e in events],[('parking',9)])

    def test_old_cap_fault_is_not_masked_by_reciprocal_fix(self):
        events=MODEL.screen(self.inputs[8048,2],self.rows,collections.Counter(),pure_cap=23)
        self.assertTrue(any(e['kind']=='quotient_cap' and e['q']==8505374 for e in events))

if __name__=='__main__':unittest.main()
