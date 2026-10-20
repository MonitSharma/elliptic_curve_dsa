import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
def git(*args):return subprocess.check_output(['git',*args],cwd=root)
assert not git('diff','--cached','--name-only').strip()
names=['local-budget','local-budget-runtime','wide-budget','wide-loan-policy','wide-generic','wide-correctness','wide-stronger-compare','wide-strong-correctness','wide-strong-generic','wide-square-budget','wide-uniform-compare','spacious-budget','primed-pool','spacious-correctness','public-schedule','public140-correctness','public140-finished','public140-final-gate','public140-nonce','public140-final','generic-lease-prover','guarded-lease-prover','scope-fingerprints','scope-clean','cross-scope-leases','certified-prefix','certified-leases']
paths=[]
for name in names:
 p=root/'experiments'/('breakthrough-'+name+'-20261020');assert p.is_dir();(p/'.gitattributes').write_bytes(b'* -text\n');(p/'.gitignore').write_bytes(b'/candidate/\n/observer/\n/primitive/\n/tool/\n/target/\n/__pycache__/\n/evidence.tar.gz\n/point-add-source.tar.gz\n');paths.append(p.relative_to(root).as_posix())
patch='experiments/autorun-20261020-breakthrough/checkpoint-public140-index.patch';git('apply','--cached','--check',patch);git('apply','--cached',patch)
helpers=['collect-width-cycle.py','prepare-seal-width-cycle.py','seal-width-cycle.py','collect-wide-diagnostics.py','compact-progress.py','direct-y15-source.rs','prepare-seal-wide-diagnostics.py','seal-public-snapshot.py','seal-wide-diagnostics.py','seal-public140-cycle.py','seal-public140-evidence.py','collect-public140-evidence.py','collect-public140-final.py','scan-certified-leases.py','prepare-wide-cache.py','run-wide-cache.py','checkpoint-public140.py','checkpoint-public140-index.patch','stage-public140.py','READY.md','LOG.md','DEVELOPMENT-NOTES.md']
paths+=['experiments/autorun-20261020-breakthrough/'+n for n in helpers]
paths+=['experiments/breakthrough-assessment-20261020/LATEST.json']
for n in ['20261020T050001Z','20261020T055829Z','20261020T062003Z']:
 p=root/'experiments/breakthrough-assessment-20261020/snapshots'/n;assert(p/'SNAPSHOT-MANIFEST.json').exists();paths.append(p.relative_to(root).as_posix())
git('add','--',*paths)
staged=git('diff','--cached','--name-only').decode().splitlines();assert all(p in ['README.md','docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']or p.startswith('experiments/')for p in staged);assert not any('resource-preflight'in p or p.endswith('/ops.bin')for p in staged);assert not any(line.startswith('160000 ')for line in git('ls-files','--stage').decode().splitlines()if any(p in line for p in paths))
bundles=[]
for p in staged:
 if p.endswith(('native-source-and-tests.tar.gz','final-evidence.tar.gz')):
  with tarfile.open(root/p)as a:
   members=a.getnames();assert not any('resource-preflight'in n or n.startswith('/')or'..'in Path(n).parts for n in members);bundles.append({'path':p,'members':len(members),'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()})
review={'staged_files':len(staged),'bundles':bundles,'public_origin':git('remote','get-url','origin').decode().strip(),'scope':'Owned complete local benchmark, final gate/source/search evidence, preserved diagnostics/negative experiments, and additive README/three-doc prefixes. Existing user changes and unrelated historical experiments excluded. No credentials or resource-preflight exports.'};assert review['public_origin']=='https://github.com/MonitSharma/elliptic_curve_dsa.git';(r/'PUBLIC140-CHECKPOINT-REVIEW.json').write_bytes((json.dumps(review,indent=2)+'\n').encode());git('add','--','experiments/autorun-20261020-breakthrough/PUBLIC140-CHECKPOINT-REVIEW.json');print(json.dumps({'staged_files':len(staged)+1,'evidence_bundles':len(bundles)}))
