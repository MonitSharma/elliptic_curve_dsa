"""Negative controls for lowest-nonce/contiguous-prefix finalization guarantees."""
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
base=Path(__file__).parent.parent/'breakthrough-public-best-drop-final-20261020'
spec=importlib.util.spec_from_file_location('product_search_verifier',base/'verify_search.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class Accounting(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.rows=[[{'nonce':k,'pass':False,'rejection_policy':'exact_full_state_only'}for k in [2,1]],[{'nonce':k,'pass':k in [4,5],'rejection_policy':'exact_full_state_only'}for k in [6,4,3,5]]];self.result={'production_screens':6,'highest_screened':6,'selected_nonce':4,'prefixes':[]}
  for i,rows in enumerate(self.rows):
   p=self.root/str(i);p.write_text(''.join(json.dumps(x)+'\n'for x in rows));self.result['prefixes'].append({'path':str(p),'first':1 if i==0 else 3,'highest':2 if i==0 else 6,'screens':len(rows),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'passes':[]if i==0 else [4,5]})
 def rewrite(self,i):
  p=Path(self.result['prefixes'][i]['path']);p.write_text(''.join(json.dumps(x)+'\n'for x in self.rows[i]));self.result['prefixes'][i]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 def rejects(self):
  with self.assertRaises(AssertionError):module.verify_search(self.result)
 def test_out_of_order_workers_still_select_lowest_pass(self):self.assertEqual(module.verify_search(self.result),[4,5])
 def test_skipped_prefix_rejected(self):self.result['prefixes'][1]['first']=4;self.rejects()
 def test_changed_rows_after_declared_hash_rejected(self):Path(self.result['prefixes'][0]['path']).write_text('changed');self.rejects()
 def test_duplicate_nonce_even_with_fresh_hash_rejected(self):self.rows[0][0]['nonce']=1;self.rewrite(0);self.rejects()
 def test_missing_lower_nonce_rejected(self):self.rows[1].pop(2);self.rewrite(1);self.rejects()
 def test_cost_selected_later_pass_rejected(self):self.result['selected_nonce']=5;self.rejects()
 def test_false_total_rejected(self):self.result['production_screens']=7;self.rejects()
 def test_false_highest_rejected(self):self.result['highest_screened']=7;self.rejects()
 def test_out_of_range_nonce_rejected(self):self.rows[1][0]['nonce']=7;self.rewrite(1);self.rejects()
 def test_nonexact_rejection_policy_rejected(self):self.rows[0][0]['rejection_policy']='approximate';self.rewrite(0);self.rejects()
if __name__=='__main__':unittest.main(verbosity=2)
