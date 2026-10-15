from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
root=Path(__file__).resolve().parent.parent/'prefilter-20261015'
expected={
 'width-supplement':'3b5faa0cf6bf60e292db91f602964a2648ea921956c9c8b3bd9017ba9270ed8d',
 'width-scope-correction':'8fa0cea26aa705f62358b80000960ab98f19a6e5ad4ca06668a22aaa1442f5a2',
 'mask-cones-supplement':'32d624bd849f7e488a780a5d701a380b09e9c8c5bbcebad041838f1f76a43d17',
 'mask-lazy-supplement':'1bf8fcce985e741ad156b5fbc6e324d3b6736acf4716e1d4f0f8c4ea3115cdfa',
 'candidate67-controls':'8433b1dd26f914e5eafdb0498c4537f939c1bfa3ab764ba0ec1e46c86495808b',
 'scalar-split-supplement':'9eddecdeb5f77498e73500a12a5f5160cf46d9502b498bbac0e7470f6fe6a5a4',
 'terminal-review-supplement':'0db4231b6b1f9026ec64c2b7963336a559d87ea3b535f7c72091a53d36667420',
 'lazy-review-negative':'12e35e90c97626a274c1d064e0377857d4280ad74751350d5e94fd8e40023690',
 'numa-affinity-supplement':'70dd36efc52560664f07fa5d77fd204e7bc072cbdf2f378746a5a5800819acd7',
 'a29-mask-supplement':'fef4d6884bd3b775ba69041d04a0efa727b78b0c187be6b17dd6f09a20e730f1',
 'a29-wholefold-supplement':'754a866dedfb9a9b50b462d57558c774b0a02c53e46f5c86efd70af904a01c78',
 'a29-square-selector-supplement':'ef0f07316274dc1f993c6e2aa09fde77a15dfa78439bdf9ab55bdc73d119cd5e',
 'a29-paired-family-components':'28848e9697a739fee2ca8d0b4bab1f32e0e17bb20f3f64d08cbec34bc8822dab',
 'a29-conditional-prefix-supplement':'df9215093c8e24070fc07b729467ac77d86d5b6499c89e3e3d299765ce78e1ea',
 'a29-conditional-transfer':'ce79b3d462f65bd1076da8e8c3c8ada831889e0f3999f297ead6ffbb0015c753',
 'repair67-composite-independent-review':'48f0efbe2f3ac3ac9308abd1030d5f27954a55b499536ed2bbeabfbda2f58f9f'}
result=[]
for stem,sha in expected.items():
 path=root/f'evidence-{stem}.tar.gz';assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
 with tarfile.open(path) as archive:
  names=archive.getnames();assert len(names)==len(set(names))
  assert all(not PurePosixPath(n.replace('\\','/')).is_absolute() and '..' not in PurePosixPath(n.replace('\\','/')).parts for n in names)
  manifest=json.load(archive.extractfile('MANIFEST.json'))
  for item in manifest['files']:
   data=archive.extractfile(item['path']).read();size=item.get('size',item.get('bytes'))
   if size is not None:assert len(data)==size,(path.name,item['path'])
   assert hashlib.sha256(data).hexdigest()==item['sha256'],(path.name,item['path'])
 refs=manifest.get('server_only_refs',manifest.get('server_only_binaries',manifest.get('server_only_hashrefs',manifest.get('server_only_or_prior_archive_hashrefs',[]))))
 result.append({'archive':path.name,'sha256':sha,'verified_files':len(manifest['files']),'hash_references_outside_this_archive':len(refs),'no_extraction_or_active_file_changes':True})
(root/'root-followup-supplement-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
