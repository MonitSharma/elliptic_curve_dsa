from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path(__file__).resolve().parent;dest=root/'wide67';tree=(dest/'candidate').resolve()
assert str(tree)=='/home/hclau/ecdsa_research/wide67-native-20261016/wide67/candidate'
assert (root/'run.exit').read_text().strip()=='0'
verified=json.loads((root/'LOCAL_SOURCE_VERIFIED.json').read_text());assert verified['status']=='FULL_BINARY_SOURCE_LOCALLY_VERIFIED'
assert hashlib.sha256((dest/'point-add-source.tar.gz').read_bytes()).hexdigest()==verified['source_archive_sha256']
assert not json.loads((dest/'census-summary.json').read_text())['failure_gate_pass']
for name,sha in json.loads((dest/'protected.json').read_text()).items():assert hashlib.sha256((tree/name).read_bytes()).hexdigest()==sha,name
assert hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()==verified['frozen_stream_sha256']
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  cwd=(proc/'cwd').resolve();args=(proc/'cmdline').read_bytes().replace(b'\x00',b' ').decode(errors='replace')
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 assert cwd!=tree and tree not in cwd.parents and str(tree) not in args,f'active process {proc.name}'
shutil.copyfile(tree/'ops.bin',dest/'native-ops.bin')
repo=root.parent/'toffoli';listing=subprocess.check_output(['git','-C',str(repo),'worktree','list','--porcelain'],text=True);assert 'worktree '+str(tree)+'\n' in listing
subprocess.run(['git','-C',str(repo),'worktree','remove','--force',str(tree)],check=True)
assert not tree.exists()
(root/'cleanup-result.json').write_text(json.dumps({'removed_only_owned_failed_native_tree':str(tree),'full_source_verified_locally':True,'no_active_process_reference':True,'large_native_ops_retained':str(dest/'native-ops.bin'),'nonce_search':False},indent=2)+'\n')
