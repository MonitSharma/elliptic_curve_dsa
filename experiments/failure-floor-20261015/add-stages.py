from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent;assert (root/'run.exit').read_text().strip()=='0'
old=root/'reverse-t0-observer';old.mkdir()
for name in ['generate.log','stream.sha256','binary.sha256','run.exit','run.pid','build.log','observer-tracked.patch','manifest.json']:
 p=root/name
 if p.exists():(old/name).write_bytes(p.read_bytes())
base=root/'observer-b3/src/point_add';(old/'payload_trace.rs').write_bytes((base/'payload_trace.rs').read_bytes());(base/'payload_trace.rs').write_bytes((root/'payload_trace.rs').read_bytes())
p=base/'leapfrog.rs';s=p.read_text();s+='\npub(crate) fn observed_preseed()->Option<Vec<QubitId>>{T6_PRESEED.with(|s|s.borrow().clone())}\n';p.write_text(s)
p=base/'mod.rs';s=p.read_text();needle='        if seams { leapfrog::divide_seamed(circ, y, x, ox); } else { leapfrog::divide(circ, y, x); }';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        payload_trace::stage(circ.op_count(),"divide",x,y,square::sub_square_offset());')
needle='        circ.set_phase("multiply");';assert s.count(needle)==1;s=s.replace(needle,'        let observed_x=leapfrog::observed_preseed().unwrap_or_else(||x.to_vec());\n        payload_trace::stage(circ.op_count(),"square",&observed_x,y,SECP256K1_P-SECP256K1_P);\n'+needle)
needle='        if seams { leapfrog::multiply_seamed(circ, y, x, ox); } else { leapfrog::multiply(circ, y, x); }';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        payload_trace::stage(circ.op_count(),"multiply",x,y,SECP256K1_P-SECP256K1_P);');p.write_text(s)
manifest=json.loads((root/'manifest.json').read_text());manifest['observer_revision']='forward/reverse fold wires; all tick kernels; exact divide/square/multiply stage boundaries including signed preseed'
manifest['source_files']={str(p.relative_to(root/'observer-b3')):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()};(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
