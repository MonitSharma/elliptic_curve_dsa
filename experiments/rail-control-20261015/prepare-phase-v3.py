"""Diagnose the first frozen zero-slope input without unioning 64 distinct cases."""
from pathlib import Path
import shutil,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'phase-audit-v3';assert not dest.exists();shutil.copytree(root/'phase-audit-v2',dest)
p=dest/'src/main.rs';s=p.read_text();needle='.filter(|(i,_)|i%2==1).take(64)';assert s.count(needle)==1
s=s.replace(needle,'.filter(|(i,_)|i%2==1).take(1).cycle().take(64)')
s=s.replace('fixed_zero_slope_inputs=64','fixed_zero_slope_inputs=1 replicated_lanes=64');p.write_text(s)
assert (dest/'src/phase_kernel.rs').read_bytes()==(root/'phase-audit/src/phase_kernel.rs').read_bytes()
(root/'phase-v3-manifest.json').write_text(json.dumps({'score':None,'scope':'First fixed zero-slope input (structured shot1), repeated across64 lanes; frozen kernel unchanged. This is counterexample localization, not a replacement correctness qualification.','source_sha256':{str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}},indent=2)+'\n')
