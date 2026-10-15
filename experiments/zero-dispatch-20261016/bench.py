from pathlib import Path
import ctypes as C, hashlib, json, statistics, time, array, random, struct
root=Path(__file__).resolve().parent
base=root.parent/'zero-mr-slice-20261016'
expected={'libzero8_slice.so':'84b73bcdee01bb537d0320f9985a682758d1076860455ad382a2ae175690ea82','tip.compact16.bin':'812f706d2edd7e821ff6c5f72db5e7e65b3f9756f562d99c1d0e1fceb007daf0'}
for name,sha in expected.items():
    assert hashlib.file_digest((base/name).open('rb'),'sha256').hexdigest()==sha
ops=array.array('B',(base/'tip.compact16.bin').read_bytes())
assert len(ops)%16==0
n=len(ops)//16;nq=1234;nb=45701
functions={}
for name,path in [('original',base/'libzero8_slice.so'),('lazy',root/'liblazy.so'),('threaded',root/'libthreaded.so')]:
    lib=C.CDLL(str(path));fn=lib.zero8_run
    fn.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t];fn.restype=C.c_int
    functions[name]=(lib,fn)
def run(name,iq,ib,code=ops,cap=4096):
    q=iq[:];b=ib[:];st=array.array('Q',[0])*(max(1,cap)*8)
    dummy=array.array('B',[0]);buffer=code if len(code) else dummy
    t=time.perf_counter();rc=functions[name][1](buffer.buffer_info()[0],len(code)//16,q.buffer_info()[0],b.buffer_info()[0],st.buffer_info()[0],cap)
    return rc,q,b,time.perf_counter()-t
rng=random.Random(0xECD5A1016)
for trial in range(16):
    q=array.array('Q',(rng.getrandbits(64) for _ in range(nq*8)));b=array.array('Q',(rng.getrandbits(64) for _ in range(nb*8)))
    reference=run('original',q,b)
    assert reference[0]==0
    for name in ['lazy','threaded']:
        result=run(name,q,b)
        assert result[0]==reference[0] and result[1]==reference[1] and result[2]==reference[2],(trial,name)
q=array.array('Q',[0])*(nq*8);b=array.array('Q',[0])*(nb*8)
fixture=root.parent/'prefilter-20261015/evidence/census-coordinates4096.tsv'
for index,row in enumerate(fixture.read_text().splitlines()[1:513]):
    word,lane=divmod(index,64);fields=row.split('\t')
    for reg,col in enumerate([4,5,6,7]):
        value=int(fields[col],16);target=q if reg<2 else b;offset=(reg%2)*256
        for bit in range(256):
            if (value>>bit)&1:target[(offset+bit)*8+word]|=1<<lane
reference=run('original',q,b)
for name in ['lazy','threaded']:
    result=run(name,q,b)
    assert result[0]==0 and result[1]==reference[1] and result[2]==reference[2],name
controls=[]
for kinds,cap,expected_rc in [([],1,0),([16],1,3),([15],0,2),([46],1,4),([255],1,4),([15],1,5),([15,16],1,0)]:
    code=array.array('B',b''.join(struct.pack('<HHHBBII',0,0,0,kind,0,0,0) for kind in kinds))
    for name in functions:assert run(name,q,b,code,cap)[0]==expected_rc,(kinds,name)
    controls.append({'kinds':kinds,'cap':cap,'return':expected_rc})
timings={name:[] for name in functions}
for trial in range(21):
    names=list(functions)
    if trial%2:names.reverse()
    for name in names:
        result=run(name,q,b);assert result[0]==0
        assert result[1]==reference[1] and result[2]==reference[2]
        timings[name].append(result[3])
report={'status':'DISABLED_COMPONENT_RUNTIME_COMPARISON','program_ops':n,'arbitrary_512_lane_states':16,'arbitrary_lanes':8192,'actual_fixture_lanes':512,'all_quantum_and_classical_words_equal':True,'controls':controls,'times_seconds':timings,'medians_seconds':{name:statistics.median(ts) for name,ts in timings.items()},'input_fixture_sha256':hashlib.file_digest(fixture.open('rb'),'sha256').hexdigest(),'binaries_sha256':{name:hashlib.file_digest(path.open('rb'),'sha256').hexdigest() for name,path in [('original',base/'libzero8_slice.so'),('lazy',root/'liblazy.so'),('threaded',root/'libthreaded.so')]},'rejection_enabled':False,'nonce_selected':None}
(root/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='times_seconds'},indent=2))
