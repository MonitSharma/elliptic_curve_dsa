from pathlib import Path
import ctypes as c,hashlib,json
r=Path(__file__).resolve().parent
source=r.parent.parent/'product-exact-20261015/repair53-native-20261016/parent-census.jsonl'
libpath=r.parent.parent/'scalar-fast-20261015/libscalar_fast_batch.so'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(libpath)=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
rows=[];batches=0
for line in source.open():
 row=json.loads(line);assert row['batch']==batches and row['shots']==64;batches+=1
 for f in row['failures']:
  rows.append((row['batch'],f))
assert batches==32768 and sum(f['value']!=0 for _,f in rows)==3553
lib=c.CDLL(str(libpath));lib.scalar_fast_fixed_init.argtypes=[c.c_uint];lib.scalar_fast_fixed_init.restype=c.c_int
lib.scalar_fast_pairs.argtypes=[c.c_uint,c.c_void_p,c.c_void_p];lib.scalar_fast_pairs.restype=c.c_int
assert lib.scalar_fast_fixed_init(20)==1
with (r/'fresh-a29-failures.tsv').open('w') as out:
 for start in range(0,len(rows),64):
  batch=rows[start:start+64]
  data=b''.join(int(f[k],16).to_bytes(32,'big') for _,f in batch for k in ['k1','k2'])
  inp=c.create_string_buffer(data);coords=c.create_string_buffer(len(batch)*192)
  assert lib.scalar_fast_pairs(len(batch),inp,coords)==1
  for i,(b,f) in enumerate(batch):
   values=[coords.raw[i*192+j*32:i*192+(j+1)*32].hex() for j in range(6)]
   out.write(f'a29-census-{b}-{f["lane"]} '+' '.join(values)+'\n')
report=dict(status='FRESH_A29_PRESERVED_FAILURE_INPUTS_RECONSTRUCTED',census_path=str(source),census_sha256=sha(source),census_batches=batches,census_shots=batches*64,source_stream_sha256='1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522',rows=len(rows),value_rows=sum(f['value']!=0 for _,f in rows),phase_rows=sum(f['phase']!=0 for _,f in rows),dirty_rows=sum(f['dirty']!=0 for _,f in rows),curve_backend=str(libpath),curve_backend_sha256=sha(libpath),curve_backend_provenance='Previously protected-Rust-validated public-input P,A,P+A fixed-base backend; no circuit or mask theorem inferred from these inputs.',fixture_sha256=sha(r/'fresh-a29-failures.tsv'))
(r/'fresh-fixture-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
