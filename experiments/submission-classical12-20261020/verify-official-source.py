"""Compare the published submission commit with the frozen local source."""
import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
final = root.parent / 'classical12-final-20261020'
freeze = json.loads((final / 'SOURCE_FREEZE.json').read_text())
workflow = json.loads((root / 'official-workflow.json').read_text())
assert workflow['head_branch'] == 'submissions/d9ae2845-b2d8-4535-8a54-6a9803fdfb19'
commit = workflow['head_sha']
assert commit == '90e777ea8242faa0acb2462c5cb5be7c318a2d64'
with urllib.request.urlopen('https://api.github.com/repos/Layr-Labs/ecdsafail-challenge/tarball/' + commit, timeout=60) as response:
    raw = response.read()
(root / 'official-source.tar.gz').write_bytes(raw)
sha = lambda b: hashlib.sha256(b).hexdigest()
files = {}
with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
    for member in archive.getmembers():
        if member.isfile():
            name = member.name.split('/', 1)[1]
            files[name] = sha(archive.extractfile(member).read())
source = {k:v for k,v in files.items() if k.startswith('src/point_add/')}
assert source == freeze['source_files']
protected = {}
tree = final / 'candidate'
import subprocess
for name in subprocess.check_output(['git', '-C', str(tree), 'ls-files']).decode().splitlines():
    if not name.startswith('src/point_add/'):
        expected = sha(subprocess.check_output(['git', '-C', str(tree), 'show', 'HEAD:' + name]))
        assert files[name] == expected, name
        protected[name] = expected
result = {'status':'OFFICIAL_PUBLISHED_SOURCE_EQUALS_FROZEN_CANDIDATE', 'commit':commit,
          'source_files_verified':len(source), 'protected_files_verified':len(protected),
          'archive_sha256':sha(raw), 'source_manifest_sha256':sha((final / 'SOURCE_FREEZE.json').read_bytes())}
(root / 'OFFICIAL-SOURCE-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
