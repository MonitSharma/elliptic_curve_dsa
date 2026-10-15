"""Preserve fixed seed/park widths and give the existing planner scratch room."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'prepare.py').read_text()
def change(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
change("root/'margin-one-b3'","root/'margin-room-b3'")
change("widened=[min(v+1,258) for v in values]","widened=[min(v+1,258) for v in values] if 2 <= len(changes) < 137 else values[:]")
change("patch=subprocess.check_output",'''p=base/'leapfrog.rs';s=p.read_text();needle='("HEO_PIN_PP_WALK_MAX_QUBITS", if C35_CAP { "1235" } else { "1236" })';assert s.count(needle)==1
p.write_text(s.replace(needle,'("HEO_PIN_PP_WALK_MAX_QUBITS", "1267")'))
patch=subprocess.check_output''')
change("root/'candidate.patch'","root/'room-candidate.patch'")
change("root/'manifest.json'","root/'room-manifest.json'")
change('Uniform +1 on all fitted rail widths, capped at 258; finite tick104 fold repair retained. No input-specific table fitting. Same 138 rounds and existing supported dynamic allocator.', 'Uniform +1 on interior fitted rail widths (ticks 2..136), capped at 258; seed/park boundary rows unchanged. Planner cap 1267, finite tick104 fold repair retained. No input-specific table fitting. Same 138 rounds and supported dynamic allocator.')
exec(compile(s,str(root/'prepare.py'),'exec'))
