"""Remove only this failed owned worktree after complete local source verification."""
from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parent;tree=(root/'wide2048/candidate').resolve()
expected=Path('/home/hclau/ecdsa_research/wide2048-native-20261016/wide2048/candidate')
assert tree==expected and tree.is_relative_to(Path('/home/hclau/ecdsa_research')) and tree.exists()
assert (root/'run.exit').read_text().strip()=='0'
review=json.loads((root/'ROOT_SOURCE_AND_CENSUS_VERIFIED.json').read_text());assert review['failed_gate_no_nonce_authorized'] and review['full_source_files']==161
assert subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip()=='5a7c390233c72133df9b591c92e43422c5892142'
source=json.loads((root/'wide2048/native-source.json').read_text())
assert {str(p.relative_to(tree)) for p in (tree/'src/point_add').rglob('*') if p.is_file()}==set(source)
for name,sha in source.items():assert hashlib.sha256((tree/name).read_bytes()).hexdigest()==sha,name
protected=json.loads((root/'wide2048/protected.json').read_text())
for name,sha in protected.items():assert hashlib.sha256((tree/name).read_bytes()).hexdigest()==sha,name
assert hashlib.sha256((root/'wide2048/point-add-source.tar.gz').read_bytes()).hexdigest()==review['full_source_archive_sha256']
changed=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines()
assert sorted(changed)==sorted(review['point_add_only_changed_paths'])
assert not subprocess.check_output(['git','-C',str(tree),'ls-files','--others','--exclude-standard'],text=True).strip()
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
    try:
        cwd=(proc/'cwd').resolve();args=(proc/'cmdline').read_bytes().split(b'\0')
    except (OSError,RuntimeError):continue
    assert not cwd.is_relative_to(tree),('active cwd',proc.name,str(cwd))
    assert not any(a.startswith(str(tree).encode()+b'/') for a in args),('active executable/argument',proc.name)
subprocess.run(['git','-C','/home/hclau/ecdsa_research/toffoli','worktree','remove','--force',str(tree)],check=True)
record={'status':'FAILED_OWNED_WORKTREE_REMOVED_AFTER_INDEPENDENT161_FILE_ARCHIVE_AND_FIXED_GATE_VERIFICATION','path':str(tree),'all_protected_and_point_add_files_rechecked':True,'no_untracked_or_active_workload_in_tree':True,'complete_source_archive_retained':True}
(root/'cleanup-receipt.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
