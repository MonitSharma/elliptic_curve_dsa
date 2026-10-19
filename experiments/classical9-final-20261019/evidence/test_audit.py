"""Exercise full-prefix accounting and fail-closed handling of corrupt logs."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('audit',Path(__file__).with_name('audit-terminal.py'));a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class AuditTests(unittest.TestCase):
    def row(self,n):return {'nonce':n,'proof_accepted':True,'witnesses_tried':1,'certified_wrong_value':True,'authoritative_rejection':True,'witness_batch':0,'witness_shot':0}
    def check(self,rows,expected=4,lane=0):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'rows.jsonl';p.write_text(''.join(json.dumps(x)+'\n' for x in rows));return a.audit_lane(p,lane,expected,look=2,workers=2)
    def test_interleaved_complete(self):self.assertEqual(self.check([self.row(n) for n in (1,2,5,6)])['rows'],4)
    def test_duplicate(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):self.check([self.row(n) for n in (1,2,5,5)])
    def test_missing(self):
        with self.assertRaisesRegex(ValueError,'missing nonce'):self.check([self.row(n) for n in (1,2,5)])
    def test_wrong_lane(self):
        with self.assertRaisesRegex(ValueError,'wrong lane'):self.check([self.row(n) for n in (1,2,3,6)])
    def test_unaccepted_proof(self):
        row=self.row(1);row['proof_accepted']=False
        with self.assertRaisesRegex(ValueError,'unaccepted'):self.check([row],2)
    def test_incomplete_protected_pass(self):
        row={'nonce':1,'proof_accepted':True,'witnesses_tried':0,'certified_wrong_value':False,'authoritative_rejection':False,'candidate_full_fallback_pass':True,'exact_early_shots':9024,'exact_early_kind':'pass','protected_shots':9023}
        with self.assertRaisesRegex(ValueError,'incomplete protected'):self.check([row],2)
if __name__=='__main__':unittest.main()
