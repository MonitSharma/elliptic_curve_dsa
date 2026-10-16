"""Extract exact original/final register annotations and physical dimensions."""
import array,collections,hashlib,json,struct,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;freeze=json.loads((r/'REPAIR67_FREEZE.json').read_text());none=(1<<64)-1
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
original=read(r/'tip/ops.bin');parent=read(r/freeze['repair_parent_stream']);after=read(r/freeze['external_stream'])
assert original['ordered_register_annotations']==parent['ordered_register_annotations']==after['ordered_register_annotations']
assert original['registers']==parent['registers']==after['registers']
assert after['qubits']==freeze['resources']['qubits']==1234 and after['classical_bits']==freeze['resources']['classical_bits']==66245
assert hashlib.sha256((r/freeze['repair_parent_stream']).read_bytes()).hexdigest()==freeze['repair_parent_sha256']
assert hashlib.sha256((r/freeze['external_stream']).read_bytes()).hexdigest()==freeze['external_stream_sha256']
row=dict(status='EXACT_REGISTER_ABI_AND_DIMENSIONS_VERIFIED',original4b_stream_sha256=hashlib.sha256((r/'tip/ops.bin').read_bytes()).hexdigest(),A29_parent_stream_sha256=freeze['repair_parent_sha256'],candidate_stream_sha256=freeze['external_stream_sha256'],same_original_ordered_register_annotations=True,original4b=original,A29_parent=parent,candidate=after,prefix_manifest=freeze['prefix_manifest'],classical_id_format='Protected Op/BitId u64; exact full/census backend u32; no u16 truncation or obsolete16-bit admission rejection.',scope='Register ordering/dimensions only. Does not assert original4b coordinate-function transfer across A29. Conditional cache mask transfer requires a separately sound A29 source-bound mask and the complete A29-relative cache certificate.',counts_scope='Static source dimensions, not executed Toffoli means or a scored record.',nonce_scope='Original frozen nonce1046072871510; a new nonce needs identical audited prefix plus48 XX pairs and candidate final-source own Fiat inputs.',score=None)
target=r/'REPAIR67_ABI.json';assert not target.exists();target.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(status=row['status'],dimensions={name:{k:obj[k] for k in ['ops','qubits','classical_bits']} for name,obj in [('original4b',original),('A29',parent),('candidate',after)]},register_lengths={k:len(v) for k,v in after['registers'].items()})),flush=True)
