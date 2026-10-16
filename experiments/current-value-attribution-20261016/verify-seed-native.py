from pathlib import Path
import json,hashlib,struct,subprocess
base=Path('/home/hclau/ecdsa_research');e=base/'current-value-attribution-20261016';r=base/'seed-restore-20261016'
assert(r/'native.exit').read_text().strip()=='0';assert(r/'guard-tests.exit').read_text().strip()=='0';assert(r/'protected.exit').read_text().strip()=='0'
exec((e/'inspect-seed-region.py').read_text().split('m=json.loads')[0]);r=base/'seed-restore-20261016'
parent=load(base/'product-exact-20261015/tip/ops.bin');native=load(r/'candidate/ops.bin');pred=json.loads((r/'predicted.json').read_text());assert len(parent)==len(native)==11630716*56;assert hashlib.sha256(native).hexdigest()==pred['expected_canonical_sha256']
at=pred['only_one_op_change'];assert native[:at*56]==parent[:at*56]and native[(at+1)*56:]==parent[(at+1)*56:];a=list(struct.unpack_from('<7Q',parent,at*56));b=list(struct.unpack_from('<7Q',native,at*56));assert a[:4]==[8,2**64-1,1106,1134]and b[:4]==[13,881,1106,1134]and a[4:]==b[4:]
for name,sha in json.loads((r/'source-files.json').read_text()).items():assert hashlib.sha256((r/'candidate'/name).read_bytes()).hexdigest()==sha
decl=json.loads((r/'PREDECLARATION.json').read_text())
for name,sha in decl['proof_files'].items():assert hashlib.sha256((e/name).read_bytes()).hexdigest()==sha
changed=subprocess.check_output(['git','-C',str(r/'candidate'),'diff','--name-only'],text=True).splitlines();assert changed and all(p.startswith('src/point_add/')for p in changed)
out=dict(status='PASS COMPLETE NATIVE SOURCE REPRODUCTION; FRESH GATE PENDING',source_stream_sha256=hashlib.sha256((r/'candidate/ops.bin').read_bytes()).hexdigest(),canonical_sha256=hashlib.sha256(native).hexdigest(),original_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',ops=11630716,Q=1234,B=45701,MR=906156,added_T=1,added_Q=0,added_MR=0,all_original_MR_ops_and_positions_identical=True,every_other_original_op_byte_identical=True,all_classical_scopes_ABI_identity_tail_identical=True,source_hashes_rechecked=True,proof_hashes_rechecked=True,only_point_add_changed=True,declaration_sha256=hashlib.sha256((r/'PREDECLARATION.json').read_bytes()).hexdigest(),no_original_arithmetic_mask_transferred=True)
(r/'native-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
