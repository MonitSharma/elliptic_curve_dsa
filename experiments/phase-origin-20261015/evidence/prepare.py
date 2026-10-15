"""Source-location observation of a native-verified phase counterexample."""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;dest=root/'origin-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root.parent/'rail-control-20261015/square-room-b3'
for rel in subprocess.check_output(['git','-C',str(source),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():
    assert rel.startswith('src/point_add/');(dest/rel).write_bytes((source/rel).read_bytes())
p=dest/'src/point_add/builder.rs';s=p.read_text();needle='    pub fn hmr(&mut self, q: QubitId, c: BitId) {';assert s.count(needle)==1
s=s.replace(needle,'''    #[track_caller]
'''+needle+'''
        if q.0==1191 && c.0==515 && self.ops.last().is_some_and(|op|op.kind==OperationType::CX && op.q_control1.0==1191 && op.q_target.0==207) {
            eprintln!("PHASE_SOURCE raw_op={} phase={} caller={} backtrace={}",self.ops.len(),self.phase,std::panic::Location::caller(),std::backtrace::Backtrace::force_capture());
        }
''');p.write_text(s)
(root/'origin.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'manifest.json').write_text(json.dumps({'score':None,'revision':rev,'scope':'Gate-inert caller/backtrace logging for the observed Hmr neighborhood. Must reproduce previous square-room stream exactly.','expected_stream_sha256':'48e2f0d8ad9bdc492415ec2700fe5dda9edc0e6f1b3a21eb935ef61ecc3953a4','changed_sha256':{rel:hashlib.sha256((dest/rel).read_bytes()).hexdigest() for rel in subprocess.check_output(['git','-C',str(dest),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()}},indent=2)+'\n')
