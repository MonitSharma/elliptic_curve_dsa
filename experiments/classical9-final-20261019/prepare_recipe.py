"""Parameterize the existing queue-only finalizer; do not launch anything."""
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'parent4-final-sat-v2-20261019'
s=(old/'finalize.py').read_text()
changes=[("native = ws / 'product-pareto-20261019/parent4-qualification'","native = ws / 'product-classical-nine-20261019'"),
 ("ws / 'product-pareto-20261019/candidate-parent4/ops.bin'","ws / 'product-classical-nine-20261019/candidate/ops.bin'"),
 ('71bbeefcfa21ea9668439210f7dfbb279e0e623aa40b33c1b7516efcb45bb43c','2932b6cf662e2d6be05679b0d5e34a9149ccbceaca57f8ce92cfccd13b8c8f6e'),
 ('9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a','76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1'),
 ('N_OPS = 17_889_606','N_OPS = 17_889_627'),
 ("json.loads((native / 'point-add-source.json').read_text())","json.loads((native / 'SOURCE_FREEZE.json').read_text())['source_files']")]
for a,b in changes:assert s.count(a)==1,a;s=s.replace(a,b)
s=s.replace("native / 'RESULT.json'","native / 'qualification/RESULT.json'").replace("native/'RESULT.json'","native/'qualification/RESULT.json'")
s=s.replace("native / 'candidate.jsonl'","native / 'qualification/candidate.jsonl'").replace('pareto-parent4-gate-20261019-v1','pareto-parent4-classical9-gate-20261019-v1')
s=s.replace("'0', '512', '6', str(out)","'0', '512', '2', str(out)")
(r/'finalize.py').write_text(s,newline='\n')
s=(old/'audit-terminal.py').read_text()
s=s.replace("ACCEPTANCE='4e3b1ce9a4f36ec1a781a5e304776a79831d6b70ff82fc248f7bb5e0c92b7ec9'","ACCEPTANCE='UNBOUND_NOT_ACCEPTED'")
s=s.replace("BINARY='0a01214ee6c245a00d39031f5103470cc833f9f66b5120d702f48831ddf537aa'","BINARY='UNBOUND_NOT_ACCEPTED'")
(r/'audit-terminal.py').write_text(s,newline='\n')
(r/'test_audit.py').write_bytes((old/'test_audit.py').read_bytes())
s=(old/'watch.py').read_text().replace("r.parent/'parent4-operational-sat-20261019'","r.parent/'product-classical-nine-operational-20261019'")
(r/'watch.py').write_text(s,newline='\n')
for p in r.glob('*.py'):compile(p.read_text(),str(p),'exec')
print('Prepared queue-only native/tail/benchmark recipe; runtime auditor remains unbound')
