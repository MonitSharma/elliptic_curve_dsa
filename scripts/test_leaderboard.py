"""Guard against reporting failed/claimed submissions or dominated points as records."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("leaderboard", Path(__file__).with_name("analyze-leaderboard.py"))
lb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lb)


def row(q, t, status="accepted", reason=None):
    return dict(id=f"{q}-{t}", officialMetrics=dict(qubits=q, toffoli=t), officialScore=q*t,
                status=status, rejectionReason=reason)


class LeaderboardTests(unittest.TestCase):
    def test_eligibility(self):
        a, b = row(3, 20), row(2, 40, "rejected", "score did not improve current best")
        inconsistent = row(1, 1)
        inconsistent["officialScore"] = 0
        self.assertEqual(lb.eligible([a, b, row(1, 1, "failed"), row(1, 1, "pending"),
            row(1, 1, "rejected", "wrong output"), inconsistent]), [a, b])

    def test_pareto_ties_and_dominance(self):
        records = [row(4, 20), row(2, 100), row(3, 80), row(3, 81), row(5, 20), row(6, 10)]
        self.assertEqual([r["id"] for r in lb.pareto(records)], ["2-100", "3-80", "4-20", "6-10"])

    def test_separate_objectives_and_strict_threshold(self):
        s = lb.analyze([row(2, 100), row(3, 30), row(10, 20)], {"mode": "scalar"})
        self.assertEqual({k: v["id"] for k, v in s["leaders"].items()},
                         dict(qubits="2-100", toffoli="10-20", product="3-30"))
        for q, t in s["targets"]["maximum_toffoli_for_product"].items():
            self.assertLess(int(q)*t, 90)
            self.assertGreaterEqual(int(q)*(t+1), 90)

    def test_empty_data_fails_closed(self):
        with self.assertRaises(ValueError):
            lb.analyze([], {})

    def test_score_only_rejection_can_set_toffoli_record(self):
        product = row(1234, 761222)
        ours = row(1464, 753771, "rejected", "score did not improve current best")
        summary = lb.analyze([product, ours], {"mode": "scalar"})
        self.assertEqual(summary["leaders"]["toffoli"]["id"], ours["id"])
        self.assertEqual(summary["leaders"]["product"]["id"], product["id"])
        self.assertEqual(summary["targets"]["maximum_toffoli"], 753770)
        self.assertEqual(summary["targets"]["maximum_toffoli_for_product"]["1464"], 641631)

    def test_local_plot_requires_complete_passing_evidence(self):
        import copy
        import json
        receipt = json.loads((Path(__file__).resolve().parents[1] /
                             "docs/data/server-verification.json").read_text())
        self.assertEqual(lb.verified_reproduction(receipt), dict(qubits=1234, toffoli=761658))
        faults = [("shots", 64), ("official_harness_unchanged", False),
                  ("classical_mismatches", 1), ("phase_garbage_batches", 1),
                  ("ancilla_garbage_batches", 1), ("stream_sha256", None)]
        for key, value in faults:
            broken = copy.deepcopy(receipt)
            broken["product_baseline"][key] = value
            self.assertIsNone(lb.verified_reproduction(broken), key)
        broken = copy.deepcopy(receipt)
        broken["product_baseline"]["score"]["score"] -= 1
        self.assertIsNone(lb.verified_reproduction(broken))
        self.assertIsNone(lb.verified_reproduction({"full_candidate": {"status": "failed_validation"}}))


if __name__ == "__main__":
    unittest.main()
