from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-core-loan-fold-20261020'
(r/'run.sh').write_bytes((old/'run.sh').read_bytes().replace(b'breakthrough-core-loan-fold',b'breakthrough-t0-shared-product').replace(b'for filter in core_loan_fold_tests',b'for filter in t0_shared_product_tests core_loan_fold_tests'))
for n in ['launch.py','sweep.py']:(r/n).write_bytes((old/n).read_bytes())
