"""Source-location observation of a native-verified phase counterexample."""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;dest=root/'origin-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root.parent/'y15-unseeded-20261015/wide-b3'
for rel in subprocess.check_output(['git','-C',str(source),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():
    assert rel.startswith('src/point_add/');(dest/rel).write_bytes((source/rel).read_bytes())
p=dest/'src/point_add/builder.rs';s=p.read_text();needle='    pub fn hmr(&mut self, q: QubitId, c: BitId) {';assert s.count(needle)==1
s=s.replace(needle,'''    #[track_caller]
'''+needle+'''
        if q.0==135 && c.0==1555 {
            eprintln!("PHASE_SOURCE raw_op={} phase={} caller={} backtrace={}",self.ops.len(),self.phase,std::panic::Location::caller(),std::backtrace::Backtrace::force_capture());
        }
''');p.write_text(s)
(root/'origin.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'manifest.json').write_text(json.dumps({'score':None,'revision':rev,'scope':'Gate-inert caller/backtrace logging for the observed Hmr neighborhood. Must reproduce the wide Y15 seedless stream exactly.','expected_stream_sha256':'0e5b5f6f2640da7e50c6bb0ae788f093d4df7fedba811007b6a2894879dd6b3e','changed_sha256':{rel:hashlib.sha256((dest/rel).read_bytes()).hexdigest() for rel in subprocess.check_output(['git','-C',str(dest),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()}},indent=2)+'\n')
