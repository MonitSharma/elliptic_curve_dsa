from pathlib import Path
import hashlib,json,subprocess,tarfile
root=Path(__file__).resolve().parent;dest=root/'product67';tree=dest/'candidate'
assert (root/'run.exit').read_text().strip()=='0'
declaration=json.loads((dest/'DECLARATION.json').read_text());expected=declaration['expected_normal_generated_stream_sha256']
assert hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()==expected
protected=json.loads((dest/'protected.json').read_text())
for name,sha in protected.items():assert hashlib.sha256((tree/name).read_bytes()).hexdigest()==sha,name
changed=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines();assert changed and all(p.startswith('src/point_add/') for p in changed)
patch=subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add']);(dest/'native-candidate.patch').write_bytes(patch)
sources={str(p.relative_to(tree)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (tree/'src/point_add').rglob('*') if p.is_file()}
(dest/'native-source.json').write_text(json.dumps(sources,indent=2)+'\n')
archive=dest/'point-add-source.tar.gz'
with tarfile.open(archive,'w:gz') as out:out.add(tree/'src/point_add',arcname='src/point_add')
census=json.loads((dest/'census-summary.json').read_text());assert census['failure_gate_pass']
result={'status':'COMPLETE_NATIVE_REPRODUCTION_AND_FRESH_FAILURE_GATE_PASS_PENDING_NONCE_BENCHMARK','stream_sha256':expected,'native_tests':4,'changed_files':changed,'protected_files_checked':len(protected),'source_files':len(sources),'full_source_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256(patch).hexdigest(),'census':census,'active_candidate_retained_for_qualification':True,'nonce_search':False,'resource_record':False}
(dest/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
