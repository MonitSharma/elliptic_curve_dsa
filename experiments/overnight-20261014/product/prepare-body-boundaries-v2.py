"""Observe both exact domains of the source's retroactive Y33 transformation."""
from pathlib import Path
import subprocess, sys
base, output, evidence = map(Path, sys.argv[1:4])
subprocess.run([sys.executable, str(Path(__file__).with_name('prepare-body-boundaries.py')), str(base), str(output), str(evidence)], check=True)
mod=(output/'mod.rs').read_text()
needle='        circ.y33_clears();'
assert mod.count(needle)==1
def mark(label):
 return '        product_body_observer::mark(circ,"'+label+'",x,y,ox,oy,seams,None);\n'
mod=mod.replace(needle,mark('before-y33')+'        product_body_observer::save_pre_y33(circ.product_observation_ops());\n'+needle+'\n'+mark('after-y33').rstrip())
(output/'mod.rs').write_text(mod,newline='\n')
observer=(output/'product_body_observer.rs').read_text()
observer+='\npub(super) fn save_pre_y33(ops:&[Op]){write_ops(ops,&Path::new(DIRECTORY).join("pre-y33.bin")).unwrap();}\n'
(output/'product_body_observer.rs').write_text(observer,newline='\n')
