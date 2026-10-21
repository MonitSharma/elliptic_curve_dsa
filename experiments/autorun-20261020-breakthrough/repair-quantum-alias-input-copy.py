from pathlib import Path
import hashlib,shutil
ex=Path(__file__).resolve().parent.parent;r=ex/'breakthrough-global-quantum-alias-v2-20261021';source=ex/'breakthrough-global-quantum-alias-20261021/official-ffe20.ops.bin';dest=r/'official-ffe20.ops.bin';expected='9185ad8965bec47212849d3569e2e4ce4ef86a2e15d0248bee392107beac4927'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert sha(source)==expected
(r/'SETUP-REPAIR.md').write_text('# Input-copy setup repair\n\nThe preparation wrapper executed its generator in the same namespace, which replaced the wrapper old variable with the semantic-tool path. Post-generation input copying therefore looked in the wrong directory and failed. Frozen source/controls were already saved correctly. Explicit immutable source/destination paths repair the absent copy; the input is the same predeclared exact official frame9185ad89. Native/fullscan outcomes unchanged and preserved; no statistical gate or nonce.\n')
if dest.exists():assert sha(dest)==expected
else:shutil.copyfile(source,dest)
assert sha(dest)==expected;print('Exact official input copied and verified')
