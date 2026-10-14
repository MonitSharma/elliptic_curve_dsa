from pathlib import Path
import subprocess,hashlib,json
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');ev=r/'evidence'
receipts=[]
for version in range(1,10):
    name=f'ht25-v{version}';tree=r/('candidate-'+name)
    if not tree.exists():continue
    patch=subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add/'])
    paths=subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--name-only'],text=True).splitlines()
    assert all(p.startswith('src/point_add/')for p in paths)
    if not (ev/('candidate-'+name+'-manifest.json')).exists():
        (ev/('candidate-'+name+'-partial.patch')).write_bytes(patch)
        binding=dict(scope='Preserved source after preparer failure; not a completed candidate',base_revision=subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip(),patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p:hashlib.sha256((tree/p).read_bytes()).hexdigest()for p in paths})
        (ev/('candidate-'+name+'-partial-source-binding.json')).write_text(json.dumps(binding,indent=2)+'\n')
    exitfile=ev/(name+'-components.exit');log=ev/(name+'-components.log')
    receipts.append(dict(version=version,wrapper_exit=exitfile.read_text().strip()if exitfile.exists()else None,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()if log.exists()else None,source_patch_sha256=hashlib.sha256(patch).hexdigest(),protected_files_modified=False))
(ev/'ht25-attempt-source-index.json').write_text(json.dumps(receipts,indent=2)+'\n')
