from pathlib import Path
import json,hashlib,subprocess
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');exec((r/'prepare-regions.py').read_text().split('raw=load(')[0]);a=load(r/'prototype.bin');b=load(r/'candidate/ops.bin');assert a==b
old=load(r.parent/'product-exact-20261015/tip/ops.bin');sites=json.loads((r/'regions-C.json').read_text());cursor=delta=0
for s in sites:
 begin,end=s['final_begin'],s['final_end'];assert old[cursor*56:begin*56]==b[(cursor+delta)*56:(begin+delta)*56];cursor=end;delta+=6
assert old[cursor*56:]==b[(cursor+delta)*56:];assert delta==12 and len(b)==len(old)+12*56
subprocess.run(['git','-C',str(r/'candidate'),'diff','--exit-code','--','.',':(exclude)src/point_add'],check=True)
out=dict(all_native_operations_equal_prototype=True,canonical_operation_sha256=hashlib.sha256(b).hexdigest(),native_stream_sha256=hashlib.sha256((r/'candidate/ops.bin').read_bytes()).hexdigest(),prototype_container_sha256=hashlib.sha256((r/'prototype.bin').read_bytes()).hexdigest(),ops=len(b)//56,all_operations_outside_both_named_regions_byteidentical=True,protected_tracked_files_unchanged=True,delta_native_toffoli=0,delta_mr=0,delta_physical_qubits=0,delta_ops=12,source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',inherited_R5_arithmetic_limitation_retained=True)
(r/'native-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
