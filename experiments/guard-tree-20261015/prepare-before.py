from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent;dst=root/'tip-before'
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(dst),'4b2ec52fc55da796aa8f5ef851290297e8706424'],check=True)
p=dst/'src/point_add/square_finish.rs';s=p.read_text();needle='if !ENABLED {return ops;}';assert s.count(needle)==1;s=s.replace(needle,'crate::write_ops(&ops,std::path::Path::new("../before-square-finish.bin")).unwrap();\nstd::process::exit(0);\n'+needle);p.write_text(s)
(root/'dump-only.patch').write_bytes(subprocess.check_output(['git','-C',str(dst),'diff','--binary']))
