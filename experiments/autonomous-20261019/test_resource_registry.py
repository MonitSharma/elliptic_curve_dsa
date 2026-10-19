import hashlib,json,tempfile,unittest
from pathlib import Path
from resource_registry import observed_job,validated_spec
class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.ws=Path(self.tmp.name);self.root=self.ws/'native-copy-cache';self.root.mkdir();self.script=self.root/'run.sh';self.script.write_text('echo research\n');self.record={'directory':self.root.name,'kind':'compute','slots':1,'entrypoint':'run.sh','pidfile':'run.pid','exitfile':'run.exit','source_hashes':{'run.sh':hashlib.sha256(self.script.read_bytes()).hexdigest()}}
    def tearDown(self):self.tmp.cleanup()
    def test_exact_source_and_live_process(self):
        spec=validated_spec(self.ws,self.record);(self.root/'run.pid').write_text('42\n');self.assertEqual(observed_job(spec,lambda p:True,lambda p:self.root,lambda p:['bash','run.sh']),42)
    def test_changed_source_refuses_even_inactive_descriptor(self):
        self.script.write_text('changed\n')
        with self.assertRaises(AssertionError):validated_spec(self.ws,self.record)
    def test_no_zero_slot_compute_or_negative_reservation(self):
        for slots in [0,-1,65,True]:
            with self.assertRaises(AssertionError):validated_spec(self.ws,{**self.record,'slots':slots})
    def test_outside_directory_and_source_refused(self):
        for record in [{**self.record,'directory':'../quantum_chemistry'},{**self.record,'source_hashes':{**self.record['source_hashes'],'../outside.py':'0'*64}}]:
            with self.assertRaises(AssertionError):validated_spec(self.ws,record)
    def test_wrong_process_or_cwd_refused(self):
        spec=validated_spec(self.ws,self.record);(self.root/'run.pid').write_text('42\n')
        with self.assertRaises(AssertionError):observed_job(spec,lambda p:True,lambda p:self.ws,lambda p:['bash','run.sh'])
        with self.assertRaises(AssertionError):observed_job(spec,lambda p:True,lambda p:self.root,lambda p:['python3','other.py'])
    def test_terminal_pid_and_missing_pid_are_not_active(self):
        spec=validated_spec(self.ws,self.record);self.assertIsNone(observed_job(spec,lambda p:True,None,None));(self.root/'run.pid').write_text('42\n');self.assertIsNone(observed_job(spec,lambda p:False,None,None))
    def test_idle_waiter_is_explicit_zero_only(self):
        self.assertEqual(validated_spec(self.ws,{**self.record,'kind':'idle','slots':0})['slots'],0)
        with self.assertRaises(AssertionError):validated_spec(self.ws,{**self.record,'kind':'idle','slots':1})
    def test_terminal_pid_reuse_is_inactive_but_live_matching_manager_stays_counted(self):
        spec=validated_spec(self.ws,self.record);(self.root/'run.pid').write_text('42\n');(self.root/'run.exit').write_text('0\n')
        self.assertIsNone(observed_job(spec,lambda p:True,lambda p:self.ws,lambda p:['unrelated']))
        self.assertEqual(observed_job(spec,lambda p:True,lambda p:self.root,lambda p:['bash','run.sh']),42)
    def test_path_like_pidfile_and_missing_entry_binding_refused(self):
        for record in [{**self.record,'pidfile':'../outside.pid'},{**self.record,'entrypoint':'unknown.sh'}]:
            with self.assertRaises(AssertionError):validated_spec(self.ws,record)
if __name__=='__main__':unittest.main()
