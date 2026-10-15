"""Independent component proof on unchanged B3 arithmetic source."""
from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'frame-proof-b3';assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
base=dest/'src/point_add';p=base/'mod.rs';p.write_text(p.read_text()+'\n#[cfg(test)] mod frame_kernel;\n#[cfg(test)] mod tests_terminal_frame;\n')
kernel=(root.parent/'arithmetic-repair-20261015/proof_kernel.rs').read_bytes();assert hashlib.sha256(kernel).hexdigest()=='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
(base/'frame_kernel.rs').write_bytes(kernel);(base/'tests_terminal_frame.rs').write_bytes((root/'tests_terminal_frame.rs').read_bytes())
candidate=root/'terminal-b3/src/point_add/modular.rs';assert candidate.read_bytes()==(base/'modular.rs').read_bytes()
(root/'proof-manifest.json').write_text(json.dumps({'revision':rev,'score':None,'scope':'Exhaustive widths1..8 integer addition with arbitrary carry-in and dirty consumer output; fixed-input/all-measurement BDD proof and protected native agreement; omitted phase fault rejected. Arithmetic source byte-identical to candidate.','modular_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'kernel_sha256':hashlib.sha256(kernel).hexdigest(),'test_sha256':hashlib.sha256((base/'tests_terminal_frame.rs').read_bytes()).hexdigest()},indent=2)+'\n')
