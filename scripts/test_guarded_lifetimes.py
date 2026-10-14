"""Independent scalar simulator checks conditional clean-boundary proofs."""
import importlib.util
import itertools
from pathlib import Path
import random
import unittest

spec = importlib.util.spec_from_file_location('guarded', Path(__file__).with_name('analyze-guarded-lifetimes.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def row(kind, target=m.NO, bit=m.NO, condition=m.NO, c1=m.NO, c2=m.NO):
    return kind, 0, c2, c1, target, bit, condition, m.NO


def check_all(program):
    """Enumerate all two input qubits, two input bits and R/Hmr outcomes."""
    random_count = sum(r[0] in (11,12) for r in program)
    proofs, identities = [], []
    abstract = m.Support((0,1), (0,1))
    for op in program:
        identities.append(abstract.inactive_quantum_gate(op)[0])
        proofs.append(abstract.step(op)[0])
    assert not abstract.stack
    for values in itertools.product((0,1), repeat=4+random_count):
        q = {0: values[0], 1: values[1]}
        bits = {0: values[2], 1: values[3]}
        outcomes = iter(values[4:])
        base, stack = 1, []
        for op, clean, identity in zip(program, proofs, identities):
            kind, _, c2, c1, target, bit, condition, _ = op
            guard = base if condition == m.NO else base & bits.get(condition,0)
            if identity:
                v = guard
                controls = (target,) if kind==7 else (c1,) if kind==8 else (c1,target) if kind==9 else (c1,c2) if kind==13 else (c1,c2,target)
                for control in controls: v &= q.get(control,0)
                assert v==0, (op,values,program)
            if kind == 15:
                stack.append(base); base &= bits.get(condition,0)
            elif kind == 16:
                base = stack.pop()
            elif kind in (6,8,13):
                v = guard
                if kind in (8,13): v &= q.get(c1,0)
                if kind == 13: v &= q.get(c2,0)
                q[target] = q.get(target,0) ^ v
            elif kind == 10 and guard:
                q[target], q[c1] = q.get(c1,0), q.get(target,0)
            elif kind in (11,12):
                random_value = next(outcomes)
                if guard:
                    q[target] = 0
                    if kind == 12: bits[bit] = random_value
                if clean:
                    assert q.get(target,0) == 0, (op, values, program)
            elif kind == 3:
                bits[bit] = bits.get(bit,0) ^ guard
            elif kind == 4 and guard:
                bits[bit] = 0
            elif kind == 5 and guard:
                bits[bit] = 1
    return proofs


class GuardedTests(unittest.TestCase):
    def test_same_condition_reset_and_dirty_counterexample(self):
        proved = [row(15,condition=0),row(8,2,c1=0),row(12,2,bit=2),row(16)]
        self.assertTrue(check_all(proved)[2])
        dirty = [row(8,2,c1=0),row(15,condition=0),row(12,2,bit=2),row(16)]
        self.assertFalse(check_all(dirty)[2])

    def test_snapshot_survives_classical_mutation(self):
        p = [row(15,condition=0),row(8,2,c1=0),row(3,bit=0),row(12,2,bit=2),row(16)]
        self.assertTrue(check_all(p)[3])
        p = [row(8,2,c1=0,condition=0),row(3,bit=0),row(12,2,bit=2,condition=0)]
        self.assertFalse(check_all(p)[2])

    def test_hmr_assignment_and_nested_selector(self):
        p = [row(12,3,bit=2,condition=0),row(15,condition=2),row(8,4,c1=0),
             row(15,condition=1),row(8,5,c1=4),row(12,5,bit=3),row(16),row(12,4,bit=4),row(16)]
        self.assertTrue(check_all(p)[5])
        self.assertTrue(check_all(p)[7])

    def test_predicate_algebra_faults_and_abi_lock(self):
        self.assertIsNone(m.conjunction(frozenset((1,)),frozenset((-1,))))
        self.assertFalse(m.implies(m.TRUE,frozenset((1,))))
        self.assertTrue(m.implies(frozenset((1,2)),frozenset((1,))))
        p = [row(2,0),row(15,condition=0),row(8,2,c1=0),row(12,2,bit=2),row(16),
             row(8,1,c1=0),row(11,1)]
        p.insert(1,row(2,bit=0))
        report=m.analyze_rows(lambda:iter(enumerate(p)))
        self.assertEqual(report['proved_conditional_clean_boundaries'],1)
        self.assertEqual(report['fixed_abi_qubits'],1)
        self.assertEqual(report['conservative_peak_live_intervals'],2)

    def test_random_programs_exhaustive_inputs_and_measurements(self):
        rng=random.Random(0xECD5A60220261014)
        cases=0
        for _ in range(400):
            p=[]; depth=0; resets=0
            for _ in range(24):
                kinds=[3,4,5,6,7,8,9,10,13,14,15,16]
                if resets<4: kinds += [11,12]
                kind=rng.choice(kinds)
                if kind==16:
                    if not depth: continue
                    p.append(row(16));depth-=1;continue
                if kind==15:
                    p.append(row(15,condition=rng.randrange(4)));depth+=1;continue
                controls=rng.sample(range(6),3)
                p.append(row(kind,controls[0] if kind>=6 else m.NO,
                             rng.randrange(4) if kind in (3,4,5,12) else m.NO,
                             rng.choice([m.NO,0,1,2,3]),controls[1] if kind in (8,9,10,13,14) else m.NO,
                             controls[2] if kind in (13,14) else m.NO))
                resets += kind in (11,12)
            p += [row(16)]*depth
            check_all(p)
            cases += 1 << (4+resets)
        self.assertGreater(cases,50000)

    def test_complementary_control_support_proves_identity(self):
        p=[row(8,2,c1=0,condition=0),row(3,bit=0),row(8,3,c1=1,condition=0),row(13,4,c1=2,c2=3),row(14,4,c1=2,c2=3)]
        check_all(p)
        state=m.Support((0,1),(0,1))
        for op in p[:3]: state.step(op)
        self.assertTrue(state.inactive_quantum_gate(p[3])[0])
        self.assertTrue(state.inactive_quantum_gate(p[4])[0])
        self.assertFalse(state.inactive_quantum_gate(row(13,4,c1=0,c2=1))[0])


if __name__=='__main__': unittest.main()
