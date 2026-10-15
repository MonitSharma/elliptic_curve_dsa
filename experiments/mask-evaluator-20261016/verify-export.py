from pathlib import Path
import ctypes as c,hashlib,json,mmap,random,struct,sys,time
root=Path(__file__).resolve().parent;binary=Path(sys.argv[1]);expected_hash=sys.argv[2];prefix=str(binary)[:-4]
assert binary.suffix=='.bin';actual_hash=hashlib.sha256(binary.read_bytes()).hexdigest();assert actual_hash==expected_hash
class Node(c.Structure):_fields_=[(n,c.c_uint32) for n in ['kind','a','b','aux']]
fn=c.CDLL(str(root/'libmask8.so')).mask8_eval;fn.argtypes=[c.POINTER(Node),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint32),c.c_size_t,c.POINTER(c.c_uint64)];fn.restype=c.c_int
handle=binary.open('rb');mapping=mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_COPY)
assert mapping[:8]==b'MRMASK01';n,np,nr=struct.unpack_from('<3Q',mapping,8);assert np==1024 and nr==512 and n<2**32;assert len(mapping)==32+n*16+nr*4
nodes=(Node*n).from_buffer(mapping,32);roots=(c.c_uint32*512).from_buffer(mapping,32+n*16)
raw=Path(prefix+'.audit-input-u64le.bin').read_bytes();expected=Path(prefix+'.audit-known-u64le.bin').read_bytes();assert len(raw)==1024*8 and len(expected)==512*8
ports=(c.c_uint64*(1024*8)).from_buffer_copy(b''.join(raw[i:i+8]*8 for i in range(0,len(raw),8)))
workspace=(c.c_uint64*(n*8))();out=(c.c_uint64*(512*8))();start=time.perf_counter();assert fn(nodes,n,ports,1024,workspace,n,roots,512,out)==0;audit_secs=time.perf_counter()-start
known=[~word&((1<<64)-1) for word in out];wanted=[word for(word,)in struct.iter_unpack('<Q',expected) for _ in range(8)];assert known==wanted,'all known-mask bits must equal independent exported audit file'
timings=[];rng=random.Random(2026101602)
for trial in range(3):
 for i in range(len(ports)):ports[i]=rng.getrandbits(64)
 start=time.perf_counter();assert fn(nodes,n,ports,1024,workspace,n,roots,512,out)==0;timings.append(time.perf_counter()-start)
assert hashlib.sha256(binary.read_bytes()).hexdigest()==expected_hash
report={'status':'ACTUAL_MASK_EXPORT_AVX512_AUDIT_PASS','binary':str(binary),'mask_sha256':actual_hash,'nodes':n,'ports':np,'roots':nr,'audit_original_inputs':32,'audit_padded_lanes_per_word':32,'packed_audit_words':4096,'all_known_mask_words_equal':True,'audit_seconds':audit_secs,'fresh_512_input_kernel_seconds':timings,'workspace_bytes':n*64,'kernel_library_sha256':hashlib.sha256((root/'libmask8.so').read_bytes()).hexdigest(),'source_semantic_certificate_required_separately':True,'nonce_search':False}
(root/'ACTUAL-EXPORT-RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
