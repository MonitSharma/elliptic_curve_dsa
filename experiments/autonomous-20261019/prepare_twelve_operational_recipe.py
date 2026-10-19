from pathlib import Path
import ast
ws=Path(__file__).resolve().parent.parent;old=ws/'product-classical-nine-operational-20261019';r=ws/'product-classical-twelve-operational-20261019';r.mkdir(exist_ok=False)
names=['prepare.py','accept.py','control.py','coordinator.py','live_snapshot.py','launch_prepare.py','launch_control.py','run-prepare.sh','run-control.sh']
changes={'product-classical-nine-operational-20261019':'product-classical-twelve-operational-20261019','product-classical-nine-filter-20261019':'product-classical-twelve-filter-20261019','product-classical-nine-proof-20261019':'product-classical-twelve-proof-20261019','product-classical-nine-20261019':'product-classical-twelve-native-20261019','76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1':'17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7','17_889_627':'17_889_635','CLASSICAL_NINE':'CLASSICAL_TWELVE','gate-v2.exit':'gate.exit','preflight_v13.py':'preflight_v15.py','classical9':'classical12','nine exact classical-control reductions':'twelve static exact reductions (executed saving is measured separately)'}
for name in names:
    s=(old/name).read_text()
    for a,b in changes.items():s=s.replace(a,b)
    if name.endswith('.py'):ast.parse(s)
    (r/name).write_text(s,newline='\n')
(r/'STATUS.md').write_text('# Qualified classical12 operational port, no production launch\n\nBoth the sole final262144-batch gate and complete disabled runtime qualification PASS. Clone the reviewed parent4 operational implementation with only candidate hash/opcount and appended exact qualification/proof bindings changed. Test ordering, build, accept the cost gate and compare the first4096 operational rows with this source own qualified prefix. Preserve every artifact. No new production search may start here until complete prefix control, fresh record/resources and an explicit clean transition preserving the current9 search. No nonce selected by Toffoli; queue only.\n')
print('Prepared source12 accepted-runtime and prefix-control recipes only')
