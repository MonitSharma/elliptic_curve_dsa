from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-fin1-fold-20261020';(r/'run.sh').write_bytes((old/'run.sh').read_bytes().replace(b'breakthrough-fin1-fold',b'breakthrough-reverse-plan7').replace(b'for filter in fin1_fold_tests',b'for filter in reverse_plan7_tests fin1_fold_tests'))
for n in ['launch.py','sweep.py']:(r/n).write_bytes((old/n).read_bytes())
