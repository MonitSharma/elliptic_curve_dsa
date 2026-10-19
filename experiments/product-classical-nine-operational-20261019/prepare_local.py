"""Copy existing coordinator/control source with explicit bounded changes."""
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'parent4-operational-sat-20261019'
for name in ['coordinator.py','control.py','live_snapshot.py']:
    s=(old/name).read_text()
    if name=='coordinator.py':
        a="root.parent/'product-pareto-20261019/candidate-parent4/ops.bin'";assert s.count(a)==1
        s=s.replace(a,"root.parent/'product-classical-nine-20261019/candidate/ops.bin'")
    elif name=='control.py':
        s=s.replace('ws / "product-pareto-20261019/candidate-parent4/ops.bin"','ws / "product-classical-nine-20261019/candidate/ops.bin"')
        s=s.replace('ws / "product-parent-sat-20261019/parent4-filter/baseline-0.jsonl"','ws / "product-classical-nine-filter-20261019/baseline-0.jsonl"')
        a='"134217728", "14",';assert s.count(a)==1;s=s.replace(a,'"134217728", "2",')
        s=s.replace('qualified parent4','qualified classical9').replace("parent4-filter's","classical9-filter's")
    (r/name).write_text(s,newline='\n')
for p in r.glob('*.py'):compile(p.read_text(),str(p),'exec')
print('Prepared bounded coordinator/control copies; all Python syntax checked')
