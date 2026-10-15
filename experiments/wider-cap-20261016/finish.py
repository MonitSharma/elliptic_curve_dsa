"""Preserve terminal identical-stream experiments, then remove owned worktrees."""
from pathlib import Path
import hashlib,json,subprocess,tarfile

root=Path(__file__).resolve().parent
assert root==Path('/home/hclau/ecdsa_research/wider-cap-20261016')
summary=json.loads((root/'build-summary.json').read_text())
assert all(not x['changed'] for x in summary['candidates'])
assert (root/'continue.exit').read_text().strip()=='0'
assert json.loads((root/'native-baseline-comparison.json').read_text())['same_failed_test_names']
receipt=[]
for name in ['cap1792','cap2048','parent-tests']:
    tree=root/name
    assert tree.resolve().parent==root and tree.is_dir()
    changed=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines()
    untracked=subprocess.check_output(['git','-C',str(tree),'ls-files','--others','--exclude-standard'],text=True).splitlines()
    assert all(p.startswith('src/point_add/') for p in changed+untracked),(name,changed,untracked)
    manifest={str(p.relative_to(tree)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (tree/'src/point_add').rglob('*') if p.is_file()}
    (root/f'{name}-source.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=root/f'{name}-point-add-source.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for p in sorted((tree/'src/point_add').rglob('*')):
            if p.is_file():t.add(p,arcname=str(p.relative_to(tree)))
    patch=subprocess.check_output(['git','-C',str(tree),'diff','HEAD'])
    (root/f'{name}-final.patch').write_bytes(patch)
    if name!='parent-tests':
        stream=hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()
        assert stream==summary['parent_stream_sha256']
    else:stream=None
    subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','remove','--force',str(tree)],check=True)
    receipt.append({'removed':str(tree),'source_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'stream_sha256':stream})
(root/'cleanup.json').write_text(json.dumps(receipt,indent=2)+'\n')
(root/'STATUS.md').write_text('''# Wider walk caps — terminal negative result

The predetermined caps 1792 and 2048 both generate the exact unchanged public
Toffoli stream at source 5a7c390233c72133df9b591c92e43422c5892142:
01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740.
The configured 1536 cap is already above the width required by this path.
No new benchmark result, census or nonce search follows from this experiment.

Both candidates pass the six dynamic allocator tests. An initial broader test
invocation yields 29 passes and three failures; the untouched parent reproduces
the same three failing test names. Raw logs and the corrected comparison are
preserved, including the first parser attempt. This is not an all-tests-pass claim.

Protected tracked files were checked byte-identical. Both candidate patches,
complete point_add source archives, source hashes and generation logs are
preserved before removal of the three owned detached worktrees.
''')
files=[p for p in root.iterdir() if p.is_file() and p.name not in ['evidence.tar.gz','manifest.json','verified-manifest.json']]
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as t:
    for p in sorted(files)+[root/'manifest.json']:t.add(p,arcname=p.name)
print('terminal identical-stream evidence archived',len(files))
