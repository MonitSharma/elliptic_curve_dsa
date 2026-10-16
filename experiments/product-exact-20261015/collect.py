import datetime, gzip, hashlib, json, shutil, subprocess, tarfile
from pathlib import Path
root=Path(__file__).resolve().parent
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
dest=root/('collected-'+stamp)
dest.mkdir(exist_ok=False)
for p in root.iterdir():
    if not p.is_file() or p.suffix in {'.bin','.gz'}:
        continue
    if p.name in {'receipt.json','collection-latest.log','evidence.sha256'}:
        continue
    if p.name=='collect.py' or p.suffix in {'.md','.rs','.in','.sh','.py','.log','.json','.jsonl','.tsv','.sha256','.pid','.exit','.err','.out','.patch','.txt'}:
        out=dest/p.name
        if p.stat().st_size>200_000:
            out=out.with_name(out.name+'.gz')
            with p.open('rb') as inp,gzip.GzipFile(filename=str(out),mode='wb',mtime=0) as output: shutil.copyfileobj(inp,output)
        else: shutil.copy2(p,out)
shutil.copytree(root/'analyzer',dest/'analyzer',ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
if (root/'exact-replay').exists():shutil.copytree(root/'exact-replay',dest/'exact-replay',ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
for name in ['follow-chain-20261016','scratch-20261016','scratch-v2-20261016','unfold-20261016','pair-expansion-20261016','flags-chain-20261016','flags-four-20261016','flags-extended-20261016','wide-compound-20261016','anchored-replay-20261016','anchored-new-20261016','product-continuation-20261016','product-to53-20261016','wide-to43-20261016','compact11-frozen-census-20261016','product25-frozen-census-20261016','product25-frozen-census-v2-20261016','product25-frozen-census-v3-20261016','wide-compound-frozen-20261016','product-smoothing-20261016','tail-precision-20261016','cached-witness-20261016','category-restore-20261016','category-restore-census-20261016','category-restore-census-v2-20261016','reduction-restore-20261016','guard-cache-20261016','guard-cache-bounded-20261016','guard-cache-weighted-20261016','scoped-cache-20261016','factor-cache-20261016','factor-witness-20261016','factored-cache-20261016']:
    source=root/name
    if not source.exists():continue
    for p in source.rglob('*'):
        if not p.is_file() or p.suffix=='.bin':continue
        out=dest/name/p.relative_to(source);out.parent.mkdir(parents=True,exist_ok=True)
        if p.stat().st_size>200_000:
            out=out.with_name(out.name+'.gz')
            with p.open('rb') as inp,gzip.GzipFile(filename=str(out),mode='wb',mtime=0) as output:shutil.copyfileobj(inp,output)
        else:shutil.copy2(p,out)
for name in ['scratch-tool','unfold-tool','flags-tool','flags-four-tool','flags-replay','anchored-replay','guard-cache-tool','guard-cache-bounded-tool','guard-cache-weighted-tool','scoped-cache-tool','scoped-replay','factor-cache-tool','factor-witness-tool','factored-cache-tool','recursive-unfold-tool','recursive-unfold-fast-tool','cache-certificate-tool','cache-certificate-v2-tool','endpoint-census-tool','endpoint-classification-tool','endpoint-proposals-tool','loan-normal-forms-tool','loan-affine-factors-tool']:
    if (root/name).exists():shutil.copytree(root/name,dest/name,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
manifest={'collected_at_utc':stamp,'snapshot_directory':dest.name,'pending_evidence_warning':'Jobs without a terminal successful exit marker are incomplete. Live logs/censuses may be prefixes; require the matching frozen source and declared fixed sample before any eligibility claim.','source_revision':subprocess.check_output(['git','-C',str(root/'tip'),'rev-parse','HEAD'],text=True).strip(),'source_status':subprocess.check_output(['git','-C',str(root/'tip'),'status','--short'],text=True),'diagnostic_only':True,'candidate_score':None,'files':{}}
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
for name in ['candidate-split128','candidate-anf512','candidate-final','wide-candidate-final','candidate-product-extendedflags','candidate-product-final25','candidate-wide-compound','candidate-product-tail-smooth','candidate-product-tail-one','candidate-product-tail-two','candidate-product-restore-deletions','candidate-product-restore-reductions','repair53-native-20261016/candidate','repair67-native-20261016/candidate']:
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
    for path in paths:
        source=tree/path
        if source.is_file():
            target=dest/'candidate_sources'/name/path
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
    if name=='candidate-wide-compound':
        row['ownership_notice']='Coordinator owns live nonce-only qualification here. Original pre-nonce frozen source/stream is bound by WIDE_COMPOUND_FREEZE.json and WIDE_COMPOUND_SOURCE_FREEZE.json; use the coordinator wide15-record-20261016 archive for final source/stream/score.'
    elif (tree/'ops.bin').exists():row['stream_sha256']=hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()
    manifest['all_candidates'][name]=row
for name in ['product53-frozen-census-20261016','wide43-scratch-20261016','wide-to67-scratch-20261016','product-to67-rank-20261016','repair-cache53-20261016','recursive-unfold-20261016','recursive-unfold-v2-20261016','recursive-unfold-fast-20261016','cache-certificate-20261016','cache-certificate-parallel-20261016','cache-certificate-retry-20261016','cache-certificate-v2-20261016','cache-certificate67-20261016','product-to95-rank-20261016','wide-to95-rank-20261016','rank-source','phasefix-cache67-20261016','wide-to151-rank-20261016','wide-largecaps-20261016','repair53-native-20261016','repair-to67-rank-20261016','repair53-universal-20261016','repair67-native-20261016','repair67-universal-20261016','endpoint-source-census-20261016','endpoint-classification-20261016','endpoint-proposals-20261016','loan-normal-forms-20261016','loan-affine-factors-20261016']:
    source=root/name
    if not source.exists():continue
    for p in source.rglob('*'):
        if 'candidate' in p.relative_to(source).parts:continue
        if not p.is_file() or (p.suffix=='.bin' and not any(part.endswith('point-add-source') for part in p.parts)):continue
        out=dest/name/p.relative_to(source);out.parent.mkdir(parents=True,exist_ok=True)
        if p.stat().st_size>200_000:
            out=out.with_name(out.name+'.gz')
            with p.open('rb') as inp,gzip.GzipFile(filename=str(out),mode='wb',mtime=0) as output:shutil.copyfileobj(inp,output)
        else:shutil.copy2(p,out)
for p in sorted(dest.rglob('*')):
    if p.is_file():manifest['files'][str(p.relative_to(dest))]=hashlib.sha256(p.read_bytes()).hexdigest()
(root/'receipt.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as archive:
    archive.add(dest,arcname='evidence')
    archive.add(root/'receipt.json',arcname='receipt.json')
print(json.dumps({'files':len(manifest['files']),'archive_bytes':(root/'evidence.tar.gz').stat().st_size}))
