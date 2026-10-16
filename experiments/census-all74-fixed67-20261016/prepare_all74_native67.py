"""Source-bound frozen exact cache output after the uniform ALL74 source pass."""
from pathlib import Path
import json,subprocess,hashlib
r=Path(__file__).resolve().parent;d=r/'all74-native67-20261016';d.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run(['python3',str(r/'consolidate_all74_cache67.py')],check=True)
freeze=json.loads((r/'ALL74_FIXED67_FREEZE.json').read_text());parent=json.loads((r/'all74-cache67-20261016/BASE_NATIVE_RECEIPT.json').read_text())
prefix=json.loads((r/'all74-cache67-20261016/stage-67-prefix.jsonl').read_text());resources=json.loads((r/'all74-cache67-20261016/stage-67-resources.jsonl').read_text());assert resources['qubits']==1234;freeze['resources']=resources
nativefreeze=d/'NATIVE_INPUT_FREEZE.json';nativefreeze.write_text(json.dumps(freeze,indent=2)+'\n')
old=r.parent/'frozen-cache-table-20261016';source=(old/'prepare.py').read_text()
changes={
 'root=Path(__file__).resolve().parent':f'root=Path({str(d)!r})',
 "up=root.parent/'product-exact-20261015'":"up=root.parent",
 "freeze=json.loads((up/'PRODUCT25_FREEZE.json').read_text())":f"freeze=json.loads(Path({str(nativefreeze)!r}).read_text())",
 "parent=up/'tip/ops.bin'":"parent=up/'all74-cache67-20261016/all74-parent.bin'",
 'pn-96==11630620':f"pn-96=={parent['pre_tail_ops']}",
 'b200178da6b06e841e384f71c2562c54b1dec09e6ef0a1c44990d408dba4e2e2':parent['pre_tail_sha3_256'],
 'fn-96==14142533':f"fn-96=={prefix['pre_tail_ops']}",
 '24027e53f377f24195d290b5d343c519156cfa3ae45f64529def428a901f8480':prefix['pre_tail_sha3_256'],
 "root.parent/'toffoli'":"up/'tip'",
 'frozen_cache25':'frozen_cache_all74_67',
 "dest=tree/'src/point_add';shutil.copy2(compressed_path,":"dest=tree/'src/point_add';shutil.copytree(up/'all74-cache67-20261016/base-point-add-source',dest,dirs_exist_ok=True);shutil.copy2(compressed_path,",
 "'prepared_source_generation_speed_experiment_not_a_new_resource_candidate'":"'NATIVE_ALL74_FIXED67_PREPARED_PENDING_BYTE_VERIFICATION'",
}
for a,b in changes.items():assert a in source,a;source=source.replace(a,b)
source=source.replace("'add','--intent-to-add','src/point_add/frozen_cache_all74_67.rs','src/point_add/frozen_cache_all74_67.bin'","'add','--intent-to-add','src/point_add'")
source=source.replace("'diff','HEAD','--','src/point_add'","'diff','--binary','HEAD','--','src/point_add'")
(d/'frozen_cache.rs.in').write_text((old/'frozen_cache.rs.in').read_text().replace('frozen_cache25','frozen_cache_all74_67'))
(d/'expanded_prepare.py').write_text(source);subprocess.run(['python3',str(d/'expanded_prepare.py')],check=True)
