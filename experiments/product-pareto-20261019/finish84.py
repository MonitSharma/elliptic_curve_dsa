"""Native port and source binding after all 84 exact audits pass."""
import ctypes,ctypes.util,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent;run=root/'continuation84'
result=json.loads((run/'RESULT.json').read_text());assert result['status']=='ALL_84_EXACT_CACHE_AUDITS_PASS'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
final=Path(result['output']);assert sha(final)==result['output_sha256']
subprocess.run(['python3',str(root/'prepare_chain.py'),'product84',str(root/'parent'),'parent-unwrapped','parent-unwrapped-retained'],check=True)
candidate=root/'candidate-product84';z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def raw(path):
    d=path.read_bytes();assert d[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',d,8)[0];b=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(b,n*56,d[16:],len(d)-16)==n*56;return b.raw
input_raw=raw(root/'parent-unwrapped-retained.ops.bin');input_count=len(input_raw)//56-96;input_hash=hashlib.sha3_256(input_raw[:-96*56]).hexdigest();tail=input_raw[-96*56:];del input_raw
output_raw=raw(final);assert output_raw[-96*56:]==tail;output_count=len(output_raw)//56;output_hash=hashlib.sha3_256(output_raw).hexdigest();del output_raw
data=final.read_bytes();data_hash=hashlib.sha3_256(data).hexdigest();(candidate/'src/point_add/frozen_product84.bin').write_bytes(data);del data
template=Path('/home/hclau/ecdsa_research/product179-native-20261017/candidate/src/point_add/frozen_cache_product179.rs').read_text()
template=template.replace('frozen_cache_product179.bin','frozen_product84.bin').replace('11630620',str(input_count)).replace('26007019',str(output_count)).replace('b200178da6b06e841e384f71c2562c54b1dec09e6ef0a1c44990d408dba4e2e2',input_hash).replace('08683f069d7f59a30f75af4dcf9bac4c19f972694fd4838e09c3729edd510602',data_hash)
(candidate/'src/point_add/frozen_product84.rs').write_text(template)
mod=candidate/'src/point_add/mod.rs';text=mod.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert text.count(needle)==1
mod.write_text(text.replace(needle,'    ops = frozen_product84::run(ops);\n'+needle)+'\nmod frozen_product84;\n')
env=os.environ.copy();env.update(CARGO_BUILD_JOBS='4',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',CARGO_TARGET_DIR=str(root/'target-native84'),RUSTFLAGS='-C target-cpu=native')
with (run/'native-tests.log').open('wb') as out:subprocess.run(['cargo','test','--release','--locked','--bin','build_circuit','frozen_product84::tests'],cwd=candidate,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
assert 'test result: ok. 4 passed' in (run/'native-tests.log').read_text(errors='replace'),'Binding tests did not all run'
with (run/'native-build.log').open('wb') as out:subprocess.run(['cargo','build','--release','--locked','--bin','build_circuit'],cwd=candidate,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
with (run/'native-generate.log').open('wb') as out:subprocess.run([str(root/'target-native84/release/build_circuit')],cwd=candidate,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
generated=raw(candidate/'ops.bin');assert hashlib.sha3_256(generated).hexdigest()==output_hash
no=(1<<64)-1;nq=0
for row in struct.iter_unpack('<7Q',generated):nq=max(nq,max((v+1 for v in row[1:4] if v!=no),default=0))
assert nq==1234;del generated
# Protected tracked files must match the public parent; all changes are point_add.
changed=subprocess.check_output(['git','-C',str(candidate),'diff','--name-only'],text=True).splitlines();assert all(p.startswith('src/point_add/') for p in changed)
tracked=subprocess.check_output(['git','-C',str(candidate),'ls-files'],text=True).splitlines()
protected={p:sha(candidate/p) for p in tracked if not p.startswith('src/point_add/')}
assert all(sha(root/'parent'/p)==h for p,h in protected.items())
(run/'protected-files.json').write_text(json.dumps(protected,indent=2)+'\n')
source_hashes={str(p.relative_to(candidate)):sha(p) for p in (candidate/'src/point_add').rglob('*') if p.is_file()}
(run/'point-add-source.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
with (run/'native-tracked.patch').open('wb') as out:subprocess.run(['git','-C',str(candidate),'diff','--binary'],stdout=out,check=True)
subprocess.run(['tar','-czf',str(run/'point-add-source.tar.gz'),'-C',str(candidate),'src/point_add'],check=True)
receipt={'status':'NATIVE_IDENTITY_AND_PROTECTED_FILES_PASS','candidate':str(candidate),'peak_qubits':nq,'stream_sha256':sha(candidate/'ops.bin'),'raw_ops_sha3_256':output_hash,'operations':output_count,'source_hashes_file':'point-add-source.json','no_scored_result':True}
(run/'NATIVE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
