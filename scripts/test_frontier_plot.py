"""Prevent failed or incomplete local evidence from entering publication plots."""
import copy
import json
from pathlib import Path
import unittest
from frontier_plot import verified_width

ROOT=Path(__file__).resolve().parents[1]
class PublicationAdmission(unittest.TestCase):
    def setUp(self):
        self.receipt=json.loads((ROOT/"experiments/verification-20261015/independent-verification.json").read_text())
    def test_complete_local_pass_is_admitted(self):
        self.assertEqual(verified_width(self.receipt),{"qubits":692,"toffoli":1481382858})
    def test_any_failure_channel_excludes_point(self):
        for channel in ("value","phase_batches","ancilla_batches"):
            r=copy.deepcopy(self.receipt);r["failures"][channel]=1
            self.assertIsNone(verified_width(r),channel)
    def test_failed_and_pending_candidates_are_excluded(self):
        for status in ("failed","pending","research_diagnostic"):
            r=copy.deepcopy(self.receipt);r["status"]=status
            self.assertIsNone(verified_width(r),status)
    def test_partial_or_unbound_evidence_is_excluded(self):
        for key,value in [("shots",64),("candidate_patch_sha256",None),
                          ("full_stream_sha256",""),("product",1),("total_executed_toffoli",1)]:
            r=copy.deepcopy(self.receipt);r[key]=value
            self.assertIsNone(verified_width(r),key)
        r=copy.deepcopy(self.receipt);r["full_stream_rescan"]["referenced_qubits"]=693
        self.assertIsNone(verified_width(r))
    def test_failed_research_receipts_are_not_scored_points(self):
        for path in ["experiments/toffoli-readiness-20261015/evidence/terminal/receipt.json",
                     "experiments/toffoli-readiness-20261015/wide-evidence/terminal/receipt.json",
                     "experiments/product-focus-20261015/evidence/candidate/terminal/receipt.json"]:
            self.assertIsNone(verified_width(json.loads((ROOT/path).read_text())),path)

if __name__=="__main__":unittest.main()
