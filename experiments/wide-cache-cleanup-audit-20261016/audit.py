from pathlib import Path
import tarfile,io,hashlib,json,re
root=Path(__file__).resolve().parent;base=root.parent/'wide15-record-20261016/evidence.tar.gz';assert hashlib.sha256(base.read_bytes()).hexdigest()=='2e568f3d8bd5093652a4e3cab91e128949fd849ede2b7d976cf8b257595d74cd'
outer=tarfile.open(base);source_archive=outer.extractfile('evidence/final-point-add-source.tar.gz').read();t=tarfile.open(fileobj=io.BytesIO(source_archive));out=root/'frozen-source';out.mkdir(exist_ok=False)
names=['src/point_add/mod.rs']+[n for n in t.getnames()if n.endswith('_cache.rs')and'exact_wide_'in n];receipts=[]
for name in names:
 data=t.extractfile(name).read();(out/Path(name).name).write_bytes(data)
 if not name.endswith('_cache.rs'):continue
 text=data.decode();render=text[text.index('fn render('):text.index('\npub fn audit(')];end=render[render.index('if let Some(js)=ends.get'):render.index('if let Some(js)=starts.get')]
 assert end.count('K::Hmr')==1 and end.count('K::CZ')==1 and 'K::CCX'not in end
 assert render.count('K::CCX')==1 and render.index('K::CCX')>render.index('if let Some(&j)=uses.get')
 receipts.append({'source':name,'sha256':hashlib.sha256(data).hexdigest(),'cleanup_hmr':1,'cleanup_conditional_CZ':1,'cleanup_CCX':0,'all_renderer_CCX_count':1,'only_CCX_role':'first-active-use compute','cleanup_source_lines':[i+1 for i,l in enumerate(text.splitlines())if 'out.push(push(valid));out.push(gate(K::Hmr' in l or 'out.push(gate(K::CZ' in l],'render_sha256':hashlib.sha256(render.encode()).hexdigest(),'cleanup_sha256':hashlib.sha256(end.encode()).hexdigest()})
calls=re.findall(r'ops = (exact_wide_stage\d+_cache)::optimize\(ops\);',(out/'mod.rs').read_text());assert len(calls)==15 and len(receipts)==8
result={'status':'ALL15_CACHE_STAGES_ALREADY_MEASUREMENT_ERASE','base_archive_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'nested_source_archive_sha256':hashlib.sha256(source_archive).hexdigest(),'stage_order':calls,'renderers':receipts,'uncompensated_cache_cleanup_CCX_families':0,'new_census_or_candidate':False};(root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
