from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile
root=Path(__file__).resolve().parent
assert (root/'run.exit').read_text().strip()=='0'
for name in ['product53','wide43']:
 dest=root/name;tree=dest/'candidate';declaration=json.loads((dest/'DECLARATION.json').read_text())
 expected=declaration['expected_normal_generated_stream_sha256'];assert hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()==expected
 protected=json.loads((dest/'protected.json').read_text())
 for rel,h in protected.items():assert hashlib.sha256((tree/rel).read_bytes()).hexdigest()==h,rel
 changed=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines()
 assert changed and all(p.startswith('src/point_add/') for p in changed)
 patch=subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add']);(dest/'native-candidate.patch').write_bytes(patch)
 sources={str(p.relative_to(tree)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (tree/'src/point_add').rglob('*') if p.is_file()}
 (dest/'native-source.json').write_text(json.dumps(sources,indent=2)+'\n')
 archive=dest/'point-add-source.tar.gz'
 with tarfile.open(archive,'w:gz') as out:out.add(tree/'src/point_add',arcname='src/point_add')
 shutil.copyfile(tree/'ops.bin',dest/'native-ops.bin')
 result={'status':'COMPLETE_NATIVE_SOURCE_REPRODUCTION_FRESH_FAILURE_GATE_FAILED','candidate':name,'base_revision':declaration['base_revision'],'stream_sha256':expected,'native_admission_tests':4,'native_generation_byte_identical_to_frozen_external_stream':True,'full_point_add_source_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256(patch).hexdigest(),'changed_files':changed,'protected_files_checked':len(protected),'nonce_search_performed':False,'resource_record':False}
 if name=='product53':
  data=json.loads((root.parent/'product-exact-20261015/product53-census-summary.json').read_text());assert not data['measured_failure_gate_pass'];result['census']=data
 else:
  data=json.loads((dest/'census-summary.json').read_text());assert not data['failure_gate_pass'];result['census']=data
 (dest/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(name,'preserved',len(sources),'source files')
