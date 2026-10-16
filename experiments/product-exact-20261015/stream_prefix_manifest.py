"""Verify the untouched 96-op identity nonce tail; hash explicit prefix records."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
sentinel=(1<<64)-1
for name in sys.argv[1:]:
    path=Path(name)
    with path.open('rb',buffering=0) as source:
        magic,n=struct.unpack('<8sQ',source.read(16));assert magic==b'QECCOPSZ' and n>=96
        proc=subprocess.Popen(['zstd','-dcq'],stdin=source,stdout=subprocess.PIPE)
        length=(n-96)*56;remaining=length;sha=hashlib.sha256();sha3=hashlib.sha3_256()
        while remaining:
            data=proc.stdout.read(min(8*1024*1024,remaining));assert data
            remaining-=len(data);sha.update(data);sha3.update(data)
        tail=proc.stdout.read();assert len(tail)==96*56 and proc.wait()==0
    words=[struct.unpack('<7Q',tail[i:i+56]) for i in range(0,len(tail),56)]
    for o in words:assert o[:3]==(6,sentinel,sentinel) and o[3]<=1 and o[4:]==(sentinel,sentinel,sentinel)
    assert all(words[2*i]==words[2*i+1] for i in range(48))
    nonce=sum(words[2*i][3]<<i for i in range(48))
    print(json.dumps({'path':name,'ops':n,'pre_tail_ops':n-96,'pre_tail_bytes':length,'pre_tail_sha256':sha.hexdigest(),'pre_tail_sha3_256':sha3.hexdigest(),'serialization':'Each operation7 little-endian u64:kind,control2,control1,target,c_target,c_condition,r_target. Kind padding is zero. Same56-byte records as protected QECCOPSZ payload.','tail_ops':96,'tail_sha256':hashlib.sha256(tail).hexdigest(),'nonce':nonce,'tail_verified_48_adjacent_XX_pairs_q0_or_q1':True}),flush=True)
