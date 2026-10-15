"""Locate the existing phase kernel's exact cap without changing its algebra or limits."""
from pathlib import Path
import shutil,hashlib,json
root=Path(__file__).resolve().parent;old=root.parent/'rail-control-20261015';dest=root/'phase-context';assert not dest.exists();shutil.copytree(old/'phase-audit-v3',dest)
p=dest/'src/phase_kernel.rs';s=p.read_text()
needle='    for (index, op) in ops.iter().enumerate() {';assert s.count(needle)==1
s=s.replace(needle,needle+'\n        (|| -> Result<(),String> {')
needle='        max_phase = max_phase.max(phase.0.len());';assert s.count(needle)==1
s=s.replace(needle,'''        Ok(())
        })().map_err(|e|format!("{e}; op={index} kind={:?} measurements={next_measurement} current_phase_terms={} max_phase_terms={max_phase} max_quantum_terms={max_quantum}",op.kind,phase.0.len()))?;
'''+needle)
p.write_text(s)
# The fixed diagnostic stream and packet are unchanged from v3.
(root/'phase-manifest.json').write_text(json.dumps({'score':None,'scope':'Error-context instrumentation only; unchanged term/work caps, recurrence, source stream and first fixed zero-slope input. Prior build/kernel preserved.','kernel_parent_sha256':hashlib.sha256((old/'phase-audit-v3/src/phase_kernel.rs').read_bytes()).hexdigest(),'source_sha256':{str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}},indent=2)+'\n')
