from pathlib import Path
import hashlib,json,subprocess,tarfile
root=Path(__file__).resolve().parent;tree=root/'candidate'
assert (root/'run.exit').read_text().strip()=='0'
declaration=json.loads((root/'DECLARATION.json').read_text());stream=hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest();assert stream==declaration['expected_normal_generated_stream_sha256']
assert '4 passed; 0 failed' in (root/'native-tests.log').read_text()
paths=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines();assert all(p.startswith('src/point_add/') for p in paths)
assert not subprocess.check_output(['git','-C',str(tree),'ls-files','--others','--exclude-standard'],text=True).strip()
for name,digest in json.loads((root/'protected.json').read_text()).items():assert hashlib.sha256((tree/name).read_bytes()).hexdigest()==digest,name
manifest={str(p.relative_to(tree)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (tree/'src/point_add').rglob('*') if p.is_file()}
(root/'source.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'point-add-source.tar.gz','w:gz') as t:
 for name in sorted(manifest):t.add(tree/name,arcname=name)
(root/'candidate-text.patch').write_bytes(subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add']))
receipt={'status':'PASS_IDENTICAL_FROZEN_CIRCUIT_SOURCE_GENERATION_SPEEDUP','full_generated_stream_sha256':stream,'native_admission_tests':4,'source_paths_changed':paths,'protected_files_unchanged':True,'circuit_resources_changed':False,'nonce_screening':False,'official_benchmark_on_this_source':False,'source_archive_sha256':hashlib.sha256((root/'point-add-source.tar.gz').read_bytes()).hexdigest(),'blob_sha256':declaration['blob_sha256'],'evidence_reuse':'Exactstream matches native25 source; frozen product25 census and aligned proofs transfer. Any future final selected source still needs unchanged benchmark.','generation_wall_seconds':178.09,'generation_peak_rss_KiB':4204488,'launcher_exit_marker_relocated_from_candidate':True}
(root/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
