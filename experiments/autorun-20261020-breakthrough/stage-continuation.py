import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
def git(*a):return subprocess.check_output(['git',*a],cwd=root)
names=['prefix27-width57','exact-branch-alias','prefix27-selective','prefix27-oneand','prefix27-cleanup11-native','prefix27-carry-loan','prefix27-room-grid','public54fc-lease','wide-tight-color','public8b-lease','public8b-repeat-generic','public8b-repeat-final-gate','public8b-repeat-nonce','public8b-repeat-final','prefix-xag-resynth'];paths=[]
for name in names:
 p=root/'experiments'/('breakthrough-'+name+'-20261020');assert p.is_dir();paths.append(p.relative_to(root).as_posix())
 p.joinpath('.gitattributes').write_bytes(b'* -text\n*.tsv whitespace=-blank-at-eol\n')
 ignore=p/'.gitignore';s=ignore.read_text()if ignore.exists()else''
 for entry in ['/candidate/','/observer/','/tool/','/primitive/','/target/','/__pycache__/','/evidence.tar.gz','/point-add-source.tar.gz','/final-evidence-before-review-log.tar.gz','*resource-preflight*','*.ops.bin']:
  if entry not in s.splitlines():s+=entry+'\n'
 ignore.write_bytes(s.encode())
owned=['CONTINUATION-0817.md','SUBMISSION-MODE.md','SUBMITTED-REPEAT.md','checkpoint-continuation.py','checkpoint-continuation-index.patch','checkpoint-repeat-submission-index.patch','checkpoint-repeat-official-index.patch','collect-continuation.py','collect-continuation-base.py','collect-width57.py','preserve-width57.py','seal-width57.py','seal-continuation.py','collect-more.py','collect-more-base.py','collect-model.py','collect-model-base.py','seal-small.py','collect-small.py','collect-small-base.py','prepare-repeat-nonce.py','prepare-repeat-final.py','collect-repeat-final.py','collect-repeat-final-base.py','record-repeat-submission.py','record-repeat-official.py','stage-continuation.py']
for name in owned:assert(r/name).exists();paths.append((r/name).relative_to(root).as_posix())
for name in ['20261020T081752Z','20261020T084401Z','20261020T085714Z','20261020T092622Z']:
 p=root/'experiments/breakthrough-assessment-20261020/snapshots'/name;assert(p/'SNAPSHOT-MANIFEST.json').exists();paths.append(p.relative_to(root).as_posix())
paths.append('experiments/breakthrough-assessment-20261020/LATEST.json')
git('add','--',*paths);staged=git('diff','--cached','--name-only').decode().splitlines();assert all(p in ['README.md','docs/AGENT_HANDOFF.md','docs/research-plan.md','docs/results-status.md']or any(p==a or p.startswith(a+'/')for a in paths)for p in staged);assert not any(p.endswith('/ops.bin')or'resource-preflight'in p or p.endswith('.pyc')for p in staged)
assert not any(line.startswith('160000 ')for line in git('ls-files','--stage','--',*paths).decode().splitlines());assert 'experiments/autorun-20261020-breakthrough/LOG.md'not in staged and 'experiments/autorun-20261020-breakthrough/READY.md'not in staged;assert 'experiments/breakthrough-public140-final-20261020/SUBMISSION-NOTE.md'not in staged
bundles=[]
for name in staged:
 if name.endswith(('native-source-and-tests.tar.gz','final-evidence.tar.gz')):
  p=root/name
  with tarfile.open(p)as a:
   members=a.getnames();assert not any(x.startswith('/')or'..'in Path(x).parts or'resource-preflight'in x for x in members)
  bundles.append({'path':name,'members':len(members),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'status':'EXPLICIT_OWNED_PATHS_REVIEWED','staged_files':len(staged),'evidence_bundles':bundles,'official_submission':'32256595-e0a3-4015-96ab-3422c866ec48','official_Q':1464,'official_T':751020,'scope':'Official source, local full verification, sole gate/nonce/benchmark evidence, exact cleanup component and preserved negatives. Four additive doc prefixes. Concurrent LOG/READY/old note, plots/data, submodule edits and unrelated untracked work excluded.'};(r/'CONTINUATION-CHECKPOINT-REVIEW.json').write_text(json.dumps(report,indent=2)+'\n');git('add','--','experiments/autorun-20261020-breakthrough/CONTINUATION-CHECKPOINT-REVIEW.json');print(json.dumps({'staged_files':len(staged)+1,'evidence_bundles':len(bundles)}))
