"""Materialize a self-contained collector from the previous verified workflow."""
from pathlib import Path
root=Path(__file__).resolve().parent;s=(root.parent/'phase-origin-20261015/collect.py').read_text()
changes={"['run.exit','combined-phase.exit','terminal.exit','proof.exit']":"['origin.exit','state.exit','unseeded.exit']","root/'equality.log'":"root/'origin-equality.log'","['origin-b3','terminal-b3','frame-proof-b3']":"['origin-b3','state-b3','unseeded-b3']","'terminal-'+family+'.log'":"'unseeded-'+family+'.log'","'TERMINAL_EXACT','TERMINAL_FRAME_CONTRACT'":"'TERMINAL_EXACT','TERMINAL_UNSEEDED','CARRY_STATE','CARRY_COMPARE','CARRY_OBSERVATION'","'Primitive proof exhausts small integer operands/carry-in, with a deterministic dirty consumer-output pattern.'":"'Carry snapshot covers one fixed zero-slope input with all-zero measurements; independent-word comparator model does not cover production fold distributions.'"}
for a,b in changes.items():assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
s=s.replace("for name in ['origin.exit','state.exit','unseeded.exit']:assert exits[name]==0,(name,exits)","for name in ['origin.exit','state.exit','unseeded.exit']:assert exits[name]==0,(name,exits)\nassert 'cap1536.exit' in exits,exits")
s=s.replace("['origin-b3','state-b3','unseeded-b3']","['origin-b3','state-b3','unseeded-b3','cap1536-b3']")
needle="receipt={'collected_at':"
s=s.replace(needle,"fixed_sets['cap1536']={family:sorted(map(int,re.findall(r'FINAL_BAD shot=(\\d+)',(root/('cap1536-'+family+'.log')).read_text()))) for family in ['independent','structured','candidate'] if (root/('cap1536-'+family+'.log')).exists()}\n"+needle)
(root/'collect.py').write_text(s)
v=(root.parent/'phase-origin-20261015/verify-local.py').read_text();(root/'verify-local.py').write_text(v)
