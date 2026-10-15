from pathlib import Path
import subprocess,shutil,json,hashlib,ctypes,ctypes.util,struct
root=Path('/home/hclau/ecdsa_research/precision-family-20261016');dest=root/'candidate';tip=root.parent/'product-exact-20261015/tip';rev='4b2ec52fc55da796aa8f5ef851290297e8706424'
assert(root/'isolated.exit').read_text().strip()=='0';assert(root/'isolated/raw-builder.sha256').read_text().split()[0]=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69'
source=json.loads((root/'FAMILY-A.json').read_text());a=json.loads((root/'isolated-analysis.json').read_text());b=json.loads((root/'interface-analysis.json').read_text());interfaces={r['tick']:r for r in b['rows']};rows=[r for r in a['rows']if not r['rejected']]
assert len(rows)==29 and all(interfaces[r['tick']]['admitted_classical_interface']and r['external_esh_equal']and not r['added_scratch']for r in rows)
admission=dict(family='A',structural_sites=len(source['records']),complete_admitted_sites=len(rows),admitted_ticks=[r['tick']for r in rows],source_capacity_rejections=[r for r in a['rows']if r['rejected']],inherited_edit_exclusions=source['excluded_inherited_overlap'],predicate='uniform+1 on all complete late-forward regions whose oldbody is byteidentical after inheritedpasses, source-generated from ORIGINAL allocator with unchanged sourcecapacity, and certified externalquantum/classical interfaces',packet_or_census_selection=False,changes_frozen_before_new_census=True)
(root/'FAMILY-A-ADMISSION.json').write_text(json.dumps(admission,indent=2)+'\n')
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
flat=bytearray();meta=[]
for r in rows:
 t=r['tick'];old=load(root/f'isolated/tick-{t}.old.bin');new=load(root/f'isolated/tick-{t}.new.bin');old_at=len(flat)//56;flat.extend(old);new_at=len(flat)//56;flat.extend(new)
 meta.append((t,r['common_prefix'],interfaces[t]['common_suffix'],r['payload_next'],len(old)//56,len(new)//56,old_at,new_at))
data=b'PRECFAM1'+struct.pack('<I',len(meta))+b''.join(struct.pack('<8I',*r)for r in meta)+flat;(root/'precision_family.bin').write_bytes(data)
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(dest),rev],check=True)
for name in['precision_family.rs','precision_family.bin']:shutil.copy2(root/name,dest/'src/point_add'/name)
p=dest/'src/point_add/mod.rs';s='mod precision_family;\n'+p.read_text();needle='    ops = apply_tail_nonce(ops, nonce);';assert s.count(needle)==1;p.write_text(s.replace(needle,needle+'\n    ops = precision_family::run(ops);'))
subprocess.run(['git','-C',str(dest),'add','-N','src/point_add/precision_family.rs','src/point_add/precision_family.bin'],check=True)
(root/'candidate-source.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'candidate-source.json').write_text(json.dumps(dict(base=rev,family_admission=admission,source_changes_only_point_add=True,all_inherited_tables_and_assertions_retained=True,files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()},protected={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[dest/'Cargo.toml',dest/'Cargo.lock',dest/'rust-toolchain.toml',dest/'src/circuit.rs',dest/'src/sim.rs',dest/'src/curve.rs',dest/'src/bin/build_circuit.rs',dest/'src/bin/eval_circuit.rs',dest/'src/lib.rs']if p.exists()}),indent=2)+'\n')
(root/'guard-tests.rs').write_text('#[path="candidate/src/circuit.rs"] mod circuit;\n#[path="precision_family.rs"] mod precision_family;\n')
print('PREPARED',len(meta),len(data),hashlib.sha256(data).hexdigest())
