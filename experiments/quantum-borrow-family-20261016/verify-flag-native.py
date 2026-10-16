from pathlib import Path
import json,hashlib,subprocess,struct
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016')
exec((r/'prepare-flag-regions.py').read_text().split('raw=load(')[0])
p=r/'candidate/ops.bin';tip=r.parent/'product-exact-20261015/tip';parent=load(tip/'ops.bin');native=load(p);sites=sorted(json.loads((r/'flag-regions.json').read_text()),key=lambda s:s['final_start']);cursor=0;offset=0
for s in sites:
 at=s['final_start'];old=load(r/f'old-flag-{s["site"]}.bin');new=load(r/f'new-flag-{s["site"]}.bin');assert parent[at*56:s['final_end']*56]==old
 assert native[cursor*56:(at+offset)*56]==parent[(cursor-offset)*56:at*56],'unrelated operations changed'
 assert native[(at+offset)*56:(at+offset+len(new)//56)*56]==new
 cursor=at+offset+len(new)//56;offset+=16
assert native[cursor*56:]==parent[(cursor-offset)*56:];assert len(native)==len(parent)+192*56
modified=subprocess.check_output(['git','-C',str(r/'candidate'),'diff','--name-only'],text=True).splitlines();assert modified and all(x.startswith('src/point_add/')for x in modified)
source=json.loads((r/'candidate-source.json').read_text())
for f,h in source['files'].items():assert hashlib.sha256((r/'candidate'/f).read_bytes()).hexdigest()==h
mr=lambda data:sum(o[0]in[11,12]for o in struct.iter_unpack('<7Q',data));toff=lambda data:sum(o[0]in[13,14]for o in struct.iter_unpack('<7Q',data))
assert mr(native)==mr(parent)+12;assert toff(native)==toff(parent)+12
out=dict(status='native complete circuit reproduced; no scored resource/failure result yet',source_revision=source['base'],sha256=hashlib.sha256(p.read_bytes()).hexdigest(),canonical_sha256=hashlib.sha256(native).hexdigest(),parent_sha256=hashlib.sha256((tip/'ops.bin').read_bytes()).hexdigest(),ops=len(native)//56,added_ops=192,added_physical_MR=12,added_generated_Toffoli=12,projected_mean_added_Toffoli='6',Q=1234,all12_regions_exact=True,all_unrelated_operations_byte_identical=True,only_point_add_changed=True,source_hashes_rechecked=True)
(r/'native-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
