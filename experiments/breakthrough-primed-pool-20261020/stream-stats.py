import hashlib,json,struct,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;rows=[];no=(1<<64)-1
for name in ['cap1536-original-plain','cap1536-uniform-plus-two-plain']:
 path=r/name/'ops.bin';mxq=mxb=-1;count=0;native=0;depth=0;weight=0.;h=hashlib.sha256()
 with path.open('rb',buffering=0)as raw:
  header=raw.read(16);assert header[:8]==b'QECCOPSZ';expected=int.from_bytes(header[8:],'little');p=subprocess.Popen(['zstd','-dc'],stdin=raw,stdout=subprocess.PIPE)
  while chunk:=p.stdout.read(56*65536):
   assert len(chunk)%56==0;h.update(chunk)
   for kind,q2,q1,q,ct,cc,reg in struct.iter_unpack('<7Q',chunk):
    count+=1
    for v in [q2,q1,q]:
     if v!=no:mxq=max(mxq,v)
    for v in [ct,cc]:
     if v!=no:mxb=max(mxb,v)
    if kind==15:depth+=1
    elif kind==16:depth-=1;assert depth>=0
    elif kind in[13,14]:native+=1;weight+=2.**(-depth-int(cc!=no))
  assert p.wait()==0 and count==expected and depth==0
 rows.append({'case':name,'operations':count,'maximum_referenced_qubit_plus_one':mxq+1,'maximum_referenced_bit_plus_one':mxb+1,'native_toffolis':native,'depth_weight_diagnostic':weight,'operation_record_sha256':h.hexdigest(),'framed_sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest()})
result={'cases':rows,'scope':'Complete-stream field scan, not executed benchmark results. Idle preallocation can inflate builder peak without increasing the highest qubit referenced in operations. No final gate, nonce or score.'};(r/'STREAM-STATS.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
