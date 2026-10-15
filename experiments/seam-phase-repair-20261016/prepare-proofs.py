from pathlib import Path
import shutil,json,hashlib,ctypes,ctypes.util,struct
r=Path('/home/hclau/ecdsa_research/seam-phase-repair-20261016');old=r.parent/'phase-localization-20261016/tool';s=r/'tool/src';(s/'bin').mkdir(parents=True,exist_ok=True);shutil.copy2(old/'Cargo.toml',r/'tool/Cargo.toml')
for name in['input_anf_dag_trace.rs','global_rng_anf_retained_masks.rs','phase_bdd.rs']:shutil.copy2(old/'src'/name,s/name)
prefix=(old/'src/bin/phase_primitive.rs').read_text().split('include!')[0]
(s/'bin/phase_primitive.rs').write_text(prefix+'include!("../input_anf_dag_trace.rs");\ninclude!("../global_rng_anf_retained_masks.rs");\ninclude!("../phase_bdd.rs");\ninclude!("../phase_primitive_body.rs");\n')
body=(old/'src/phase_primitive_body.rs').read_text()
body=body.replace('let mut cursor=2;let mut u=', 'let prepend=if ops[2].kind==CX&&ops[2].q_target.0 as usize==measured&&ops[2].c_condition.0!=u64::MAX{Some((ops[2].q_control1.0 as usize,ops[2].c_condition.0 as usize))}else{None};let mut cursor=2+usize::from(prepend.is_some());let mut u=')
body=body.replace('let mut carry=borrow.map_or(GlobalAnf::constant(0),|w|initial[w].clone());','let mut carry=if let Some((w,bit))=prepend{a.and(&initial[w],&b[bit])}else{borrow.map_or(GlobalAnf::constant(0),|w|initial[w].clone())};')
body=body.replace('let mut ordered=Vec::new();if let Some(w)=borrow','let mut ordered=Vec::new();if let Some((w,bit))=prepend{order.insert(b[bit].0[0].1,0);ordered.push(w);}if let Some(w)=borrow')
body=body.replace('for seed in 0..4{let mut rng=seeded(seed);','let mut ib=vec![0u64;nb as usize];for bit in &cbits{let mut raw=[0;8];XofReader::read(&mut init_rng,&mut raw);ib[*bit]=u64::from_le_bytes(raw);}for seed in 0..4{let mut rng=seeded(seed);')
body=body.replace('let mut ci=borrow.map_or(0,|w|iq[w]);','let mut ci=if let Some((w,bit))=prepend{iq[w]&ib[bit]}else{borrow.map_or(0,|w|iq[w])};')
body=body.replace('s.qubits.copy_from_slice(&iq);s.phase=','s.qubits.copy_from_slice(&iq);s.bits.copy_from_slice(&ib);s.phase=')
body=body.replace('"borrow":borrow,','"borrow":borrow,"classical_prepend":prepend,')
(s/'phase_primitive_body.rs').write_text(body)
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;z.ZSTD_compressBound.argtypes=[ctypes.c_size_t];z.ZSTD_compressBound.restype=ctypes.c_size_t;z.ZSTD_compress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int];z.ZSTD_compress.restype=ctypes.c_size_t
d=(r/'new-component.bin').read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;rows=list(struct.iter_unpack('<7Q',o.raw));meta=json.loads((r/'region.json').read_text());index=meta['first_carry_phase_cz_local']+2;assert rows[index][0]==9 and rows[index][2]==meta['measured_and_borrow_target'];row=list(rows[index]);row[2]=meta['u'][0];rows[index]=tuple(row);raw=b''.join(struct.pack('<7Q',*row)for row in rows);bound=z.ZSTD_compressBound(len(raw));out=ctypes.create_string_buffer(bound);size=z.ZSTD_compress(out,bound,raw,len(raw),3);(r/'negative-wrong-clifford.bin').write_bytes(b'QECCOPSZ'+struct.pack('<Q',len(rows))+out.raw[:size])
(r/'proof-source-hashes.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in s.rglob('*.rs')},indent=2)+'\n')
