from pathlib import Path
import ctypes as c,hashlib,json,shutil,struct,subprocess,itertools
root=Path(__file__).resolve().parent;N=(1<<64)-1
lib=c.CDLL('libzstd.so.1');lib.ZSTD_compressBound.argtypes=[c.c_size_t];lib.ZSTD_compressBound.restype=c.c_size_t;lib.ZSTD_compress.argtypes=[c.c_void_p,c.c_size_t,c.c_void_p,c.c_size_t,c.c_int];lib.ZSTD_compress.restype=c.c_size_t
def op(k,t=N,a=N,b=N,bt=N,cc=N):return(k,b,a,t,bt,cc,N)
first=op(13,3,0,1);last=op(13,3,0,2)
cases=[('positive',[first,last],1),('control_read_allowed',[first,op(8,4,0),last],1),('target_phase_read',[first,op(7,3),last],0),('old_control_write',[first,op(6,0),last],0),('new_control_write',[first,op(6,2),last],0),('identical_products',[first,first],0),('changed_direct_guard',[op(13,3,0,1,cc=0),op(3,bt=0),op(13,3,0,2,cc=0)],0),('captured_guard_survives_current_bit_change',[op(15,cc=0),first,op(3,bt=0),last,op(16)],1),('scope_fence',[first,op(15,cc=0),op(16),last],0),('at_distance64',[first]+[op(0)]*64+[last],1),('beyond_distance64',[first]+[op(0)]*65+[last],0),('measurement_read',[first,op(12,3,bt=4),last],0)]
rows=[]
for name,ops,expected in cases:
 directory=root/'controls'/name;directory.mkdir(parents=True,exist_ok=False);raw=b''.join(struct.pack('<7Q',*o)for o in ops);out=c.create_string_buffer(lib.ZSTD_compressBound(len(raw)));size=lib.ZSTD_compress(out,len(out),raw,len(raw),3);blob=b'QECCOPSZ'+struct.pack('<Q',len(ops))+out.raw[:size];source=directory/'fixture.bin';source.write_bytes(blob)
 (directory/'DECLARATION.json').write_text(json.dumps({'stream':str(source),'stream_sha256':hashlib.sha256(blob).hexdigest()}));shutil.copyfile(root/'census.py',directory/'census.py');subprocess.run(['python3',str(directory/'census.py')],check=True,stdout=subprocess.DEVNULL)
 result=json.loads((directory/'RESULT.json').read_text());assert result['eligible_pairs']==expected,(name,result);rows.append({'case':name,'expected_pairs':expected,'actual_pairs':result['eligible_pairs']})
# Exhaustive reversible permutation identity, including arbitrary dirty target.
for a,b,other,t,guard in itertools.product([0,1],repeat=5):
 old=t^(guard&a&b)^(guard&a&other);scratch=b^(guard&other);new=t^(guard&a&scratch);scratch^=guard&other;assert (new,scratch)==(old,b)
result={'status':'ALL_SCANNER_CONTROLS_AND_EXACT_IDENTITY_PASS','cases':rows,'dirty_target_basis_and_guard_cases':32,'same_scanner_sha256':hashlib.sha256((root/'census.py').read_bytes()).hexdigest(),'candidate_generated':False,'sampling':False}
(root/'CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
