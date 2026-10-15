"""Archive source attribution plus the random-event-aligned state observation."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'wide-phase-20261015/collect.py').read_text()
s=s.replace("['origin.exit']","['origin.exit','state.exit']").replace("['origin-b3']","['origin-b3','state-b3']")
s=s.replace("'HEO_TOTAL'","'HEO_TOTAL','JOINT_SITE','JOINT_STATE','JOINT_EXACT','JOINT_COMPARE','JOINT_OBSERVATION','JOINT_MEASUREMENT_VERIFIED'")
s=s.replace("'status':'terminal gate-inert source observation; not a candidate benchmark'","'status':'terminal source and raw-state observations; no candidate score'")
s=s.replace('Allocator tests establish bookkeeping invariants, not quantum cleanliness; fixed replay checks dirty ancillas separately.','The source observer is byte-identical; the state observer uses a raw pre-Y33 stream. Its fixed input and two assignments are checked against the protected simulator.')
(root/'collect.py').write_text(s)
