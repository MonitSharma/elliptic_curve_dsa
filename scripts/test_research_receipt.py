"""Admission faults: stale scores, partial evidence, protected edits and new files."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("receipt", Path(__file__).with_name("research-receipt.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src/point_add").mkdir(parents=True)
        (self.repo / "src/point_add/mod.rs").write_text("// baseline\n")
        (self.repo / "benchmark.sh").write_text("# protected fixture\n")
        self.run_git("init", "-q")
        self.run_git("add", ".")
        self.run_git("-c", "user.name=Receipt Test", "-c", "user.email=receipt@example.invalid",
                     "commit", "-qm", "fixture")
        self.log = self.root / "run.log"
        self.log.write_text("classical mismatches : 0\nphase-garbage batches : 0\n"
                            "ancilla-garbage batches : 0\nall 9024 shots OK\n")
        self.exit = self.root / "run.exit"
        self.exit.write_text("0\n")
        self.stream = self.root / "ops.bin"
        self.stream.write_bytes(b"fixture, not a quantum stream")
        self.score = self.root / "score.json"
        self.score.write_text(json.dumps({"metrics": {"qubits": 1234, "toffoli": 761658},
                                          "score": 939885972}))

    def run_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], stderr=subprocess.STDOUT)

    def collect(self, full=True):
        return MODULE.collect(self.repo, self.root / "evidence", self.log, self.exit,
                              self.stream, self.score, full)

    def test_diagnostic_never_admits_a_score(self):
        report = self.collect(False)
        self.assertEqual(report["status"], "completed_diagnostic")
        self.assertIsNone(report["qualified_score"])

    def test_failure_rejects_stale_passing_score(self):
        self.exit.write_text("1\n")
        report = self.collect()
        self.assertEqual(report["status"], "failed")
        self.assertIsNone(report["qualified_score"])

    def test_partial_success_and_protected_change_reject(self):
        self.log.write_text("all 64 shots OK\n")
        self.assertEqual(self.collect()["status"], "incomplete_or_inadmissible_evidence")
        self.log.write_text("classical mismatches : 0\nphase-garbage batches : 0\n"
                            "ancilla-garbage batches : 0\nall 9024 shots OK\n")
        (self.repo / "benchmark.sh").write_text("# changed protected harness\n")
        report = self.collect()
        self.assertEqual(report["protected_tracked_changes"], ["benchmark.sh"])
        self.assertIsNone(report["qualified_score"])

    def test_new_source_is_preserved_in_patch_without_staging(self):
        (self.repo / "src/point_add/new.rs").write_text("// new candidate\n")
        report = self.collect()
        self.assertIn("src/point_add/new.rs", report["source_sha256"])
        self.assertIn(b"+// new candidate", (self.root / "evidence/candidate.patch").read_bytes())
        self.assertEqual(self.run_git("diff", "--cached"), b"")
        (self.repo / "src/point_add/new.rs").unlink()
        self.run_git("apply", "--check", str(self.root / "evidence/candidate.patch"))


if __name__ == "__main__":
    unittest.main()
