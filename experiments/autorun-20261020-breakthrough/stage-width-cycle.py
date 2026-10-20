import json,subprocess,tarfile
from pathlib import Path
r=Path(__file__).resolve().parents[2];a=r/'experiments/autorun-20261020-breakthrough'
def git(*args):return subprocess.check_output(['git',*args],cwd=r)
assert not git('diff','--cached','--name-only').strip();patch='experiments/autorun-20261020-breakthrough/checkpoint-width-index.patch';git('apply','--cached','--check',patch);git('apply','--cached',patch)
names=['t0-shared-product','fin1-loan-native','fin1-fold','reverse-plan7','reverse-budget','generic-postpass','truth14','replay-layout-audit','sparse-polynomial','width-correctness','local-budget']
paths=[f'experiments/breakthrough-{n}-20261020'for n in names]
paths+=['experiments/breakthrough-core-loan-preflight-20261020','experiments/breakthrough-assessment-20261020/LATEST.json','experiments/breakthrough-assessment-20261020/snapshots/20261020T040024Z']
paths+=['experiments/autorun-20261020-breakthrough/'+n for n in ['DEVELOPMENT-NOTES.md','LOG.md','T0-SHARED-PRODUCT-PLAN.md','prepare-seal-core-loan-native.py','seal-core-loan-native.py','collect-core-loan-native.py','prepare-seal-width-cycle.py','seal-width-cycle.py','collect-width-cycle.py','document-width-cycle.py','checkpoint-width-cycle.py','checkpoint-width-index.patch','finish-width-checkpoint.py','stage-width-cycle.py','seal-width-correctness.py']]
paths+=['experiments/breakthrough-live-core-rank-20261020/'+n for n in ['FIN1-MODEL.json','fin1-model.py','retained-cubic-cleanup.py','RETAINED-CUBIC-CLEANUP.json','retained-cubic-hard-first.py','RETAINED-CUBIC-HARD-FIRST.json','retained-external-carry.py','RETAINED-EXTERNAL-CARRY.json','retained-carry-first.py','RETAINED-CARRY-FIRST.json']]
git('add','--',*paths)
staged=git('diff','--cached','--name-only').decode().splitlines();assert all(p in ['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']or p.startswith('experiments/')for p in staged);assert not any('resource-preflight'in p or p.endswith('/ops.bin')for p in staged)
bundles=[]
for path in staged:
 if path.endswith('native-source-and-tests.tar.gz'):
  with tarfile.open(r/path)as archive:
   files=archive.getnames();assert not any('resource-preflight'in p for p in files);bundles.append({'path':path,'members':len(files)})
receipt={'staged_files':len(staged),'bundles':bundles,'public_origin':git('remote','get-url','origin').decode().strip(),'scope':'Only owned additive research evidence and three additive documentation prefixes. Existing user changes excluded. Public origin and push authority verified in prior cycle; no credentials or resource-preflight artifacts.'};(a/'WIDTH-CHECKPOINT-REVIEW.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());git('add','--','experiments/autorun-20261020-breakthrough/WIDTH-CHECKPOINT-REVIEW.json');print(json.dumps(receipt))
