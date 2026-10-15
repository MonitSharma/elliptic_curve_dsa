from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parent
assert root==Path('/home/hclau/ecdsa_research/frozen-next-20261016')
receipt=json.loads((root/'LOCAL_ARCHIVE_VERIFIED.json').read_text());assert receipt['all_inner_and_outer_source_hashes_match']
assert hashlib.sha256((root/'evidence.tar.gz').read_bytes()).hexdigest()==receipt['outer_archive_sha256']
assert (root/'run.exit').read_text().strip()=='0'
for name in ['product53','wide43']:
 tree=(root/name/'candidate').resolve();assert tree.parent==root/name and tree.name=='candidate'
 result=json.loads((root/name/'RESULT.json').read_text());assert not result['nonce_search_performed']
 assert hashlib.sha256((root/name/'native-ops.bin').read_bytes()).hexdigest()==result['stream_sha256']
 sources=json.loads((root/name/'native-source.json').read_text());protected=json.loads((root/name/'protected.json').read_text())
 for rel,h in {**sources,**protected}.items():assert hashlib.sha256((tree/rel).read_bytes()).hexdigest()==h,rel
 assert hashlib.sha256((root/name/'point-add-source.tar.gz').read_bytes()).hexdigest()==result['full_point_add_source_archive_sha256']
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  for entry in ['cwd','exe']:
   try:target=(proc/entry).resolve(strict=True)
   except (OSError,RuntimeError):continue
   assert target!=tree and tree not in target.parents,(proc.name,entry,str(target))
 subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','remove','--force',str(tree)],check=True)
 print('Removed archived owned detached tree',tree)
(root/'cleanup-result.json').write_text(json.dumps({'status':'two_archived_owned_detached_trees_removed','protected_and_source_hashes_verified':True,'no_active_process_cwd_or_executable':True,'trees':['product53/candidate','wide43/candidate']},indent=2)+'\n')
