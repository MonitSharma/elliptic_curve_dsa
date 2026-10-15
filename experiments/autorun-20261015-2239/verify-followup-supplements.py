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
 'terminal-review-supplement':'0db4231b6b1f9026ec64c2b7963336a559d87ea3b535f7c72091a53d36667420'}
result=[]
for stem,sha in expected.items():
 path=root/f'evidence-{stem}.tar.gz';assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
 with tarfile.open(path) as archive:
  names=archive.getnames();assert len(names)==len(set(names))
  assert all(not PurePosixPath(n.replace('\\','/')).is_absolute() and '..' not in PurePosixPath(n.replace('\\','/')).parts for n in names)
  manifest=json.load(archive.extractfile('MANIFEST.json'))
  for item in manifest['files']:
   data=archive.extractfile(item['path']).read();assert len(data)==item.get('size',item.get('bytes'));assert hashlib.sha256(data).hexdigest()==item['sha256'],item['path']
 result.append({'archive':path.name,'sha256':sha,'verified_files':len(manifest['files']),'server_refs_not_downloaded':len(manifest.get('server_only_refs',manifest.get('server_only_binaries',[]))),'no_extraction_or_active_file_changes':True})
(root/'root-followup-supplement-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
