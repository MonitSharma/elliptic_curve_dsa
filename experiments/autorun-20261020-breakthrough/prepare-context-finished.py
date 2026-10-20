from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-context-lease-finished-20261020';r.mkdir(exist_ok=True);assert not(r/'run.py').exists()
for filename in['.gitattributes','.gitignore']:shutil.copyfile(root/'experiments/breakthrough-public322-square-finished-20261020'/filename,r/filename)
shutil.copyfile(root/'experiments/breakthrough-public322-square-finished-20261020/cache-template.rs',r/'cache-template.rs')
source=(root/'experiments/breakthrough-public322-square-finished-20261020/run.py').read_text();source=source.replace("filters=['square_lease_cache'","filters=['context_lease_cache','square_lease_cache'").replace('counts==[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]','counts==[1,1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]').replace('SQUARE1408_FINISHED_NONCE0_NOT_GATED_OR_SCORED','CONTEXT213_FINISHED_NONCE0_NOT_GATED_OR_SCORED');(r/'run.py').write_text(source)
(r/'PLAN.md').write_text('''# Finish213 exact earlier-context product leases

Parent is official a4ee/T750911, sourcebe2902c2, locally byte-verified source
28e443bc and exact full stream54c8cd60. The new proof engine passes7 native
controls/faults; component scan independently accepts213 unconditional leases,
213 diagnostic T saving, maximum donor1479. Extra width is permitted for the
independent Toffoli objective. This does not beat the new public product record.

Preserve the complete parent constructor unchanged, rename only its entrypoint,
call it and bind the ENTIRE exact parent stream before stripping96 checked
identity-tail ops. Apply the213 separately generated lease rows, bind every
canonical output record to the independent proof output, then run the unchanged
generic exact pipeline and append nonce0. Old parent's square binding and153
cache module remain unchanged. Freeze all198 source files and17 protected files
before generation. Run28 native controls, including both cache modules. A fresh
exact-public comparison and its own sole declared32768-batch final gate are
required before any nonce screening or unchanged benchmark. No past gate reused.
''')
print(r)
