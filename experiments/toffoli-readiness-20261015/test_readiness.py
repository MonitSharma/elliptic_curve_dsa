import unittest
from check_readiness import assess

class IndependentRecords(unittest.TestCase):
    def setUp(self):
        self.frontier={'leaders':{'qubits':{'officialMetrics':{'qubits':693}},
            'toffoli':{'officialMetrics':{'toffoli':761156}},'product':{'officialScore':939396074}}}
        self.receipt={'status':'passed','exit_status':0,'protected_tracked_changes':[]}
        self.replay={'independent':dict(unequal_batches=0,right_bad=0,right_phase_batches=0,right_dirty_batches=0)}
    def test_toffoli_record_without_product_record(self):
        result=assess(self.frontier,self.receipt,{'score':1235*761155,'metrics':{'qubits':1235,'toffoli':761155}},self.replay)
        self.assertEqual(result['record_improvements'],['toffoli'])
        self.assertEqual(result['status'],'READY_FOR_PACKAGING')
    def test_failed_evaluation_never_promotes_diagnostic_counts(self):
        self.receipt.update(status='failed',exit_status=1)
        result=assess(self.frontier,self.receipt,{'score':1,'metrics':{'qubits':1,'toffoli':1}},self.replay)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertIsNone(result['qualified_metrics'])
    def test_known_independent_failure_blocks_packaging(self):
        self.replay['independent']['right_bad']=1
        result=assess(self.frontier,self.receipt,{'score':1235*761155,'metrics':{'qubits':1235,'toffoli':761155}},self.replay)
        self.assertEqual(result['status'],'BLOCKED')
    def test_equal_record_is_not_an_improvement(self):
        result=assess(self.frontier,self.receipt,{'score':1235*761156,'metrics':{'qubits':1235,'toffoli':761156}},self.replay)
        self.assertEqual(result['status'],'BLOCKED')

if __name__=='__main__':unittest.main()
