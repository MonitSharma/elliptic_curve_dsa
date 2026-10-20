import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
def git(*a):return subprocess.check_output(['git',*a],cwd=root)
assert not git('diff','--cached','--name-only').strip();patch='experiments/autorun-20261020-breakthrough/checkpoint-exact154-index.patch';git('apply','--cached','--check',patch);git('apply','--cached',patch)
names=['public140-cache','public140-cone-cache','public140-parent-4045','public140-exact154','public140-exact154-final-gate','public140-exact154-final','prefix-dag','prefix27-native','prefix27-fold-native','prefix27-production','prefix27-global-reuse','prefix27-width57'];paths=[]
for name in names:
 p=root/'experiments'/('breakthrough-'+name+'-20261020');assert p.is_dir();(p/'.gitattributes').write_bytes(b'* -text\n*.tsv whitespace=-blank-at-eol\n');(p/'.gitignore').write_bytes(b'/candidate/\n/observer/\n/primitive/\n/tool/\n/target/\n/__pycache__/\n/evidence.tar.gz\n/point-add-source.tar.gz\n');paths.append(p.relative_to(root).as_posix())
(r/'.gitignore').write_bytes(b'/__pycache__/\n*.pyc\n');paths.append('experiments/autorun-20261020-breakthrough');paths.append('experiments/breakthrough-assessment-20261020/LATEST.json')
for n in ['20261020T064008Z','20261020T072008Z','20261020T074818Z']:
 p=root/'experiments/breakthrough-assessment-20261020/snapshots'/n;assert(p/'SNAPSHOT-MANIFEST.json').exists();paths.append(p.relative_to(root).as_posix())
git('add','--',*paths);staged=git('diff','--cached','--name-only').decode().splitlines();assert all(p in ['README.md','docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']or p.startswith('experiments/')for p in staged);assert not any('resource-preflight'in p or p.endswith('/ops.bin')or p.endswith('.pyc')for p in staged);assert 'experiments/breakthrough-public140-final-20261020/SUBMISSION-NOTE.md'not in staged
assert not any(x.startswith('160000 ')for x in git('ls-files','--stage','--',*paths).decode().splitlines());bundles=[]
for p in staged:
 if p.endswith(('native-source-and-tests.tar.gz','final-evidence.tar.gz')):
  with tarfile.open(root/p)as a:
   members=a.getnames();assert not any('resource-preflight'in x or x.startswith('/')or'..'in Path(x).parts for x in members);bundles.append({'path':p,'members':len(members),'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()})
review={'staged_files':len(staged),'evidence_bundles':bundles,'public_origin':git('remote','get-url','origin').decode().strip(),'scope':'Owned verified exact154 result and gate/source/nonce evidence, native-prefix research and preserved negatives. Four additive documentation prefixes only. Existing plots/data/submodules and externally edited old submission note excluded. No credentials or resource-preflight exports.'};assert review['public_origin']=='https://github.com/MonitSharma/elliptic_curve_dsa.git';(r/'EXACT154-CHECKPOINT-REVIEW.json').write_bytes((json.dumps(review,indent=2)+'\n').encode());git('add','--','experiments/autorun-20261020-breakthrough/EXACT154-CHECKPOINT-REVIEW.json');print(json.dumps({'staged_files':len(staged)+1,'evidence_bundles':len(bundles)}))
