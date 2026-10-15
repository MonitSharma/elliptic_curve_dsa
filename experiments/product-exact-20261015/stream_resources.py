"""Read dimensions from immutable QECCOPSZ streams without Python packages."""
import array,json,struct,subprocess,sys
from pathlib import Path
sentinel=(1<<64)-1
for name in sys.argv[1:]:
    path=Path(name)
    if not path.exists():
        print(json.dumps({'path':name,'missing':True}));continue
    count=0;maxq=maxb=maxr=-1
    with path.open('rb',buffering=0) as source:
        magic,n=struct.unpack('<8sQ',source.read(16));assert magic==b'QECCOPSZ'
        proc=subprocess.Popen(['zstd','-dcq'],stdin=source,stdout=subprocess.PIPE)
        remainder=b''
        while True:
            chunk=proc.stdout.read(56*100000)
            if not chunk:break
            chunk=remainder+chunk;length=len(chunk)//56*56;remainder=chunk[length:]
            data=array.array('Q');data.frombytes(chunk[:length])
            if sys.byteorder!='little':data.byteswap()
            count+=len(data)//7
            for offset in [1,2,3]:maxq=max(maxq,max((x for x in data[offset::7] if x!=sentinel),default=-1))
            for offset in [4,5]:maxb=max(maxb,max((x for x in data[offset::7] if x!=sentinel),default=-1))
            maxr=max(maxr,max((x for x in data[6::7] if x!=sentinel),default=-1))
        assert not remainder and count==n and proc.wait()==0
    print(json.dumps({'path':name,'ops':n,'qubits':maxq+1,'classical_bits':maxb+1,'registers':maxr+1,'u16_physical_ids_supported':max(maxq,maxb)<65535}),flush=True)
