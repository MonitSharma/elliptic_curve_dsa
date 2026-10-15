"""Build an explicit list of owned reviewed artifacts; excludes shared foreign work."""
from pathlib import Path
import json,subprocess
repo=Path(__file__).resolve().parents[2]
paths=set()
def add(name):
    p=repo/name;assert p.is_file(),name
    assert p.stat().st_size<40*1024*1024,(name,'large artifact requires separate review')
    paths.add(p.relative_to(repo).as_posix())
for name in ['docs/AGENT_HANDOFF.md','docs/results-status.md','docs/research-plan.md','docs/SERVER_HANDOFF.md',
 'experiments/autorun-20261015-2239/LOG.md','experiments/autorun-20261015-2239/verify-followup-supplements.py',
 'experiments/autorun-20261015-2239/verify-conditional-prefix.py','experiments/autorun-20261015-2239/verify-final67-append.py',
 'experiments/autorun-20261015-2239/verify-current-attribution.py',
 'experiments/autorun-20261015-2239/checkpoint-paths-0654.py','experiments/autorun-20261015-2239/followup-supplements-0654.log']:
    add(name)
for folder in ['global-scope-proposals-20261016','guard-snapshot-20261016','repair67-conditional-filter-20261016']:
    for p in (repo/'experiments'/folder).rglob('*'):
        if p.is_file() and not {'__pycache__','target'}.intersection(p.parts):add(p.relative_to(repo))
pref='experiments/prefilter-20261015/'
for stem in ['a29-square-selector-supplement','a29-paired-family-components','a29-conditional-prefix-supplement','a29-conditional-transfer','repair67-composite-independent-review']:
    add(pref+f'evidence-{stem}.tar.gz')
for stem in ['a29-square-selector','a29-paired-family','a29-conditional-prefix','a29-conditional-transfer']:
    add(pref+f'evidence/{stem}-archive-receipt.json')
for name in ['root-followup-supplement-verification.json','archive-a29-square-selector-evidence.py','archive-a29-paired-family-evidence.py','archive-a29-conditional-prefix-evidence.py','archive-a29-conditional-transfer-evidence.py','freeze-a29-conditional-transfer.py','a29-conditional-prefix-v1/ROOT_INDEPENDENT_REVIEW.json','a29-conditional-prefix-v1/INDUCTION.md']:
    add(pref+name)
for folder in ['a29-conditional-certificate-v1','repair67-composite-review-v1']:
    for p in (repo/pref/folder).rglob('*'):
        if p.is_file() and p.suffix in ['.json','.md','.py','.rs']:add(p.relative_to(repo))
product='experiments/product-exact-20261015/'
for name in ['STATUS.md','collect.py','PRODUCT95_FREEZE.json','ENDPOINT-PRODUCT-NEGATIVE.md','ENDPOINT-PRODUCT-OBLIGATIONS.md','audit_endpoint_proposals.py','FINALPROOF95_INCREMENTAL_VERIFIED.json','REPAIR67_RUNTIME_REVIEW.md','make_followup_incremental.py','verify_followup_incremental.py','run-finalproof95-followup.sh','finalproof95-followup-verification.log','finalproof95-followup-full-verification.log','supplement-finalproof95-endpoint-20261016.delivery.json','supplement-finalproof95-endpoint-20261016.tar.gz']:
    add(product+name)
for p in (repo/product/'repair67-universal-20261016').glob('*'):
    if p.is_file() and p.suffix in ['.json','.md','.log']:add(p.relative_to(repo))
for folder in ['endpoint-source-census-20261016','endpoint-classification-20261016','endpoint-proposals-20261016']:
    for name in ['RESULTS.json','INDEPENDENT_BOUNDS_DONOR_GUARDS.json','DECLARATION.json']:
        if (repo/product/folder/name).exists():add(product+folder+'/'+name)
for name in ['ROOT_CHECKPOINT_VERIFIED.json','checkpoint-evidence.tar.gz','checkpoint-receipt.json']:
    add('experiments/product25-operational-20261016/'+name)
for name in ['attribution-checkpoint-v1.tar.gz','attribution-checkpoint-v1-receipt.json','attribution-checkpoint-v1-local-verification.json','ATTRIBUTION-CHECKPOINT.md','N2-DIAGNOSIS.json','ROOT_ATTRIBUTION_REVIEW.json','verify-attribution-checkpoint.py','collect-attribution-checkpoint.py']:
    add('experiments/current-value-attribution-20261016/'+name)
paths=sorted(paths)
assert not any(p=='README.md' or 'submission-20261016/' in p or 'prefilter-macro-' in p for p in paths)
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo,text=True).strip(),'foreign/stale index contents; do not modify'
base=Path(__file__).with_suffix('')
base.with_suffix('.json').write_text(json.dumps(paths,indent=2)+'\n')
base.with_suffix('.nul').write_bytes(b'\0'.join(p.encode() for p in paths)+b'\0')
print(json.dumps({'owned_paths':len(paths),'total_bytes':sum((repo/p).stat().st_size for p in paths),'excludes_shared_README_and_foreign_submission':True}))
