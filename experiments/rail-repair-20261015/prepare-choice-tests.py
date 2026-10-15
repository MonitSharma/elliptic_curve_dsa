from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'choice-tests-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
base=dest/'src/point_add'
kernel=root.parent/'arithmetic-repair-20261015/proof_kernel.rs';(base/'rail_kernel.rs').write_bytes(kernel.read_bytes())
p=base/'mod.rs';p.write_text('#[cfg(test)] mod rail_kernel;\n'+p.read_text())
p=base/'leapfrog.rs';p.write_text(p.read_text()+'\n'+(root/'rail_choice_tests.rs').read_text())
(root/'choice-tests.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'choice-kernel.sha256').write_text(hashlib.sha256(kernel.read_bytes()).hexdigest()+'  rail_kernel.rs\n')
