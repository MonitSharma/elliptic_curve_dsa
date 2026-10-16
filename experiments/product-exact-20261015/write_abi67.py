"""Extract exact original/final register annotations and physical dimensions."""
import array,collections,hashlib,json,struct,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;freeze=json.loads((r/'PRODUCT67_FREEZE.json').read_text());none=(1<<64)-1
def read(path):
    counts=collections.Counter();regs={};records=[];maxq=maxb=-1;seen=0
    with path.open('rb',buffering=0) as source:
        magic,n=struct.unpack('<8sQ',source.read(16));assert magic==b'QECCOPSZ'
        proc=subprocess.Popen(['zstd','-dcq'],stdin=source,stdout=subprocess.PIPE)
        while True:
            chunk=proc.stdout.read(56*65536)
            if not chunk:break
            assert len(chunk)%56==0
            words=array.array('Q');words.frombytes(chunk)
            if sys.byteorder!='little':words.byteswap()
            for j in range(0,len(words),7):
                k,a,b,t,bt,c,reg=words[j:j+7];counts[k]+=1;seen+=1
                maxq=max([maxq]+[q for q in [a,b,t] if q!=none]);maxb=max([maxb]+[bit for bit in [bt,c] if bit!=none])
                if k==1:regs.setdefault(reg,[]);records.append([k,a,b,t,bt,c,reg])
                if k==2:
                    assert (t==none)!=(bt==none);regs.setdefault(reg,[]).append({'kind':'qubit' if t!=none else 'classical','id':t if t!=none else bt});records.append([k,a,b,t,bt,c,reg])
        assert seen==n and proc.wait()==0
    return {'ops':n,'qubits':maxq+1,'classical_bits':maxb+1,'opcode_counts':dict(counts),'registers':regs,'ordered_register_annotations':records}
before=read(r/'tip/ops.bin');after=read(r/freeze['external_stream']);assert before['ordered_register_annotations']==after['ordered_register_annotations'] and before['registers']==after['registers']
assert after['qubits']==1234 and after['classical_bits']==54995
row={'status':'EXACT_REGISTER_ABI_AND_DIMENSIONS_VERIFIED','original_stream_sha256':hashlib.sha256((r/'tip/ops.bin').read_bytes()).hexdigest(),'candidate_stream_sha256':freeze['external_stream_sha256'],'same_original_ordered_register_annotations':True,'original':before,'candidate':after,'prefix_manifest':freeze['prefix_manifest'],'classical_id_format':'ProtectedOp/BitId is u64; root full/census backend supports32-bit classical IDs. No16-bit truncation.','counts_scope':'Opcode counts are static source dimensions, not executed Toffoli means or a resource record.','nonce_scope':'This binds frozen original nonce1046072871510. A differentnonce requires exact prefix+48XX validation and finalownFiat inputs.','score':None}
target=r/'PRODUCT67_ABI.json';assert not target.exists();target.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'status':row['status'],'original_dimensions':{k:before[k] for k in ['ops','qubits','classical_bits']},'candidate_dimensions':{k:after[k] for k in ['ops','qubits','classical_bits']},'register_lengths':{k:len(v) for k,v in after['registers'].items()}}),flush=True)
