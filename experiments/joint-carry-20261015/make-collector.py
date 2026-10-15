"""Preserve both preparation attempts and the exact-carry observer."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'dynamic-pool-20261015/collect.py').read_text()
a=s.index('for name in [');b=s.index('for p in sorted(root.iterdir()):',a)
s=s[:a]+"assert exits.get('state.exit')==1,exits\nassert exits.get('state2.exit')==101,exits\nassert exits.get('state3.exit')==0,exits\nassert exits.get('state4.exit')==0,exits\nassert (root/'state3-b3/ops.bin').read_bytes()==(root/'state4-b3/ops.bin').read_bytes()\n"+s[b:]
s=s.replace("['control-b3','wide-b3']","['state-b3','state2-b3','state3-b3','state4-b3']")
s=s.replace("'HEO_TOTAL'","'HEO_TOTAL','JOINT_SITE','JOINT_STATE','JOINT_EXACT','JOINT_COMPARE','JOINT_OBSERVATION','JOINT_MEASUREMENT_VERIFIED'")
a=s.index('fixed_sets=');b=s.index("receipt={'collected_at':",a);s=s[:a]+"fixed_sets={}\n"+s[b:]
s=s.replace("'source_trace_byte_identical':True","'source_trace_byte_identical':False")
s=s.replace("'fixed_wrong_sets':fixed_sets","'raw_observer_streams_identical':True,'invalidated_evidence':{'state3.log':'Flip indexed Hmr only, omitting random reads from R. Not the intended measurement counterexample.'},'fixed_wrong_sets':fixed_sets")
s=s.replace('Allocator tests establish bookkeeping invariants, not quantum cleanliness; fixed replay checks dirty ancillas separately.','Raw observer is compared against the protected simulator on one fixed input for two measurement assignments. The finite model omits folds and has no quantum cost or phase proof.')
(root/'collect.py').write_text(s)
(root/'verify-local.py').write_text((root.parent/'dynamic-pool-20261015/verify-local.py').read_text())
