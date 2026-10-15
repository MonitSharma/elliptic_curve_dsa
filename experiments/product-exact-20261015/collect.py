import gzip, hashlib, json, shutil, subprocess, tarfile
from pathlib import Path
root=Path(__file__).resolve().parent
dest=root/'collected'
dest.mkdir(exist_ok=True)
for p in root.iterdir():
    if not p.is_file() or p.suffix in {'.bin','.gz'}:
        continue
    if p.name=='collect.py' or p.suffix in {'.md','.rs','.sh','.py','.log','.json','.jsonl','.tsv','.sha256','.pid','.exit','.err','.out','.patch','.txt'}:
        out=dest/p.name
        if p.stat().st_size>200_000:
            out=out.with_name(out.name+'.gz')
            with p.open('rb') as inp,gzip.open(out,'wb') as output: shutil.copyfileobj(inp,output)
        else: shutil.copy2(p,out)
shutil.copytree(root/'analyzer',dest/'analyzer',ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
if (root/'exact-replay').exists():shutil.copytree(root/'exact-replay',dest/'exact-replay',ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
for name in ['follow-chain-20261016','scratch-20261016','scratch-v2-20261016','unfold-20261016','pair-expansion-20261016','flags-chain-20261016','flags-four-20261016','flags-extended-20261016','wide-compound-20261016','anchored-replay-20261016','anchored-new-20261016']:
    source=root/name
    if not source.exists():continue
    for p in source.rglob('*'):
        if not p.is_file() or p.suffix=='.bin':continue
        out=dest/name/p.relative_to(source);out.parent.mkdir(parents=True,exist_ok=True)
        if p.stat().st_size>200_000:
            out=out.with_name(out.name+'.gz')
            with p.open('rb') as inp,gzip.open(out,'wb') as output:shutil.copyfileobj(inp,output)
        else:shutil.copy2(p,out)
for name in ['scratch-tool','unfold-tool','flags-tool','flags-four-tool','flags-replay','anchored-replay']:
    if (root/name).exists():shutil.copytree(root/name,dest/name,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
manifest={'source_revision':subprocess.check_output(['git','-C',str(root/'tip'),'rev-parse','HEAD'],text=True).strip(),'source_status':subprocess.check_output(['git','-C',str(root/'tip'),'status','--short'],text=True),'diagnostic_only':True,'candidate_score':None,'files':{}}
protected={}
tracked=subprocess.check_output(['git','-C',str(root/'tip'),'ls-files'],text=True).splitlines()
for name in tracked:
    p=root/'tip'/name
    if name.startswith('src/point_add/') or not p.is_file():continue
    protected[name]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest['protected_files_sha256']=protected
dependency=root.parent/'overnight-20261014/product-b3-baseline'
manifest['analyzer_dependency_revision']=subprocess.check_output(['git','-C',str(dependency),'rev-parse','HEAD'],text=True).strip()
manifest['protected_dependency_mismatches']=[name for name in protected if name.startswith('src/') and (dependency/name).is_file() and hashlib.sha256((dependency/name).read_bytes()).hexdigest()!=protected[name]]
candidate=root/'candidate-split128'
if candidate.exists():
    manifest['candidate_base_revision']=subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD'],text=True).strip()
    manifest['candidate_diff_paths']=subprocess.check_output(['git','-C',str(candidate),'diff','--name-only'],text=True).splitlines()
    assert all(p.startswith('src/point_add/') for p in manifest['candidate_diff_paths'])
    manifest['candidate_protected_mismatches']=[name for name,value in protected.items() if (candidate/name).is_file() and hashlib.sha256((candidate/name).read_bytes()).hexdigest()!=value]
manifest['all_candidates']={}
for name in ['candidate-split128','candidate-anf512','candidate-final','wide-candidate-final','candidate-product-extendedflags']:
    tree=root/name
    if not tree.exists():continue
    paths=subprocess.check_output(['git','-C',str(tree),'diff','--name-only'],text=True).splitlines()
    assert all(p.startswith('src/point_add/') for p in paths)
    mismatches=[]
    for path in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
        if path.startswith('src/point_add/') or not (tree/path).is_file():continue
        original=subprocess.run(['git','-C',str(tree),'show','HEAD:'+path],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        if original.returncode==0 and hashlib.sha256(original.stdout).hexdigest()!=hashlib.sha256((tree/path).read_bytes()).hexdigest():mismatches.append(path)
    row={'base_revision':subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip(),'diff_paths':paths,'protected_mismatches':mismatches}
    if (tree/'ops.bin').exists():row['stream_sha256']=hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()
    manifest['all_candidates'][name]=row
for p in sorted(dest.rglob('*')):
    if p.is_file():manifest['files'][str(p.relative_to(dest))]=hashlib.sha256(p.read_bytes()).hexdigest()
(root/'receipt.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as archive:
    archive.add(dest,arcname='evidence')
    archive.add(root/'receipt.json',arcname='receipt.json')
print(json.dumps({'files':len(manifest['files']),'archive_bytes':(root/'evidence.tar.gz').stat().st_size}))
