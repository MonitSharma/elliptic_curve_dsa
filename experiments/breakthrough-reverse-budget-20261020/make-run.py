from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-reverse-plan7-20261020';(r/'run.sh').write_bytes((old/'run.sh').read_bytes().replace(b'breakthrough-reverse-plan7',b'breakthrough-reverse-budget').replace(b'for filter in reverse_plan7_tests',b'for filter in reverse_budget_tests'))
for n in ['launch.py','sweep.py']:(r/n).write_bytes((old/n).read_bytes())
