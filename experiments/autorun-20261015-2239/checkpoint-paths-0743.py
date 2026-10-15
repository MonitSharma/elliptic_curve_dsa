"""List only owned terminal evidence; exclude live/shared work and binary caches."""
from pathlib import Path
import json,subprocess
repo=Path(__file__).resolve().parents[2];paths=set()
def add(name):
 p=repo/name;assert p.is_file(),name;assert p.stat().st_size<40*1024**2,name
 paths.add(p.relative_to(repo).as_posix())
for name in ['docs/AGENT_HANDOFF.md','docs/SERVER_HANDOFF.md','docs/research-plan.md','docs/results-status.md','docs/data/latest-leaderboard.json','docs/frontier-results.md','docs/figures/frontier.png','docs/figures/frontier.svg',
 'experiments/autorun-20261015-2239/LOG.md','experiments/autorun-20261015-2239/checkpoint-0743.py','experiments/autorun-20261015-2239/checkpoint-paths-0743.py','experiments/autorun-20261015-2239/ROOT_PHASE_RETENTION_REVIEW.json','experiments/autorun-20261015-2239/ROOT_WIDE_SOURCE_NEGATIVES_REVIEW.json']:
 add(name)
for name in ['verify-repair67-filter.py','verify-repair67-fused.py','verify-repair67-cost.py','verify-fused-guard.py','verify-phase-and-retention.py','verify-square4-terminal.py','verify-seed-diagnosis.py']:
 add('experiments/autorun-20261015-2239/'+name)
for folder in ['guard-fused-20261016','repair67-conditional-filter-20261016','repair67-fused-filter-20261016','repair67-operational-20261016','repair67-cost-20261016','n2-loan-retention-20261016','rail-tail64-20261016','wide-quadratic-factor-20261016','wide-guard-cofactor-20261016','wide-global-classification-20261016','value-carry-contracts-20261016']:
 for p in (repo/'experiments'/folder).rglob('*'):
  if p.is_file() and not {'.git','__pycache__','target','root-data'}.intersection(p.parts):add(p.relative_to(repo))
for name in ['checkpoint-evidence.tar.gz','checkpoint-receipt.json','ROOT_CHECKPOINT_VERIFIED.json']:
 add('experiments/product25-operational-20261016/'+name)
for name in ['phase-attribution-addendum-v2.tar.gz','phase-attribution-addendum-v2-receipt.json','phase-attribution-addendum-v2-local-verification.json','seed-diagnosis-v1.tar.gz','seed-diagnosis-v1-receipt.json','seed-diagnosis-v1-local-verification.json','ROOT_SEED_DIAGNOSIS_REVIEW.json']:
 add('experiments/current-value-attribution-20261016/'+name)
for name in ['supplement-loan-dirty-rhs-20261016.tar.gz','supplement-loan-dirty-rhs-20261016.delivery.json','ROOT_LOAN_RHS_DELIVERY_REVIEW.json','N2-DIRTY-RHS-NEGATIVE.md','loan-rhs-followup-full-verification.log','loan-rhs-followup-verification.log','audit_loan_return_zeros.py','loan_affine_factors.rs.in','loan_queries.rs.in','prepare_loan_affine_factors.py','prepare_loan_normal_forms.py','run-loan-affine-factors.sh','run-loan-normal-forms.sh','run-loan-rhs-followup.sh']:
 add('experiments/product-exact-20261015/'+name)
for name in ['evidence-guard-fused-component.tar.gz','evidence-repair67-operational-source-proposal-v2.tar.gz','evidence-seed-independent-review-v2.tar.gz','evidence/guard-fused-archive-receipt.json','seed-review-20261016/REVIEW.json','seed-review-20261016/REVIEWED-GENERATOR-SOURCES.json']:
 add('experiments/prefilter-20261015/'+name)
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo,text=True).strip(),'Preserve foreign index'
assert all(p!='README.md' and 'submission-20261016/' not in p and 'prefilter-macro-' not in p for p in paths)
ignored=subprocess.run(['git','check-ignore','--stdin'],cwd=repo,input='\n'.join(paths)+'\n',text=True,capture_output=True)
assert not ignored.stdout.strip(),ignored.stdout
paths=sorted(paths);base=Path(__file__).with_suffix('');base.with_suffix('.json').write_text(json.dumps(paths,indent=2)+'\n');base.with_suffix('.nul').write_bytes(b'\0'.join(p.encode()for p in paths)+b'\0')
subprocess.run(['git','diff','--check','--',*paths],cwd=repo,check=True)
print(json.dumps(dict(owned_paths=len(paths),bytes=sum((repo/p).stat().st_size for p in paths),foreign_README_submission_and_live_seed_profile_work_excluded=True)))
