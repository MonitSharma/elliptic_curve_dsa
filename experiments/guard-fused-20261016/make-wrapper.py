from pathlib import Path
import hashlib,struct,json
d=Path(__file__).resolve().parent;r=d.parent/'prefilter-20261015'
path=r/'a29-conditional-prefix-v1/public-discrepancy-guard.bin';data=path.read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(data)=='355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3'
assert data[:8]==b'MRMASK01';n,np,nr=struct.unpack_from('<QQQ',data,8)
assert(n,np,nr)==(1831784,1024,1) and len(data)==32+16*n+4
root=struct.unpack_from('<I',data,32+16*n)[0];assert root<n
for i in range(n):
 k,a,b,aux=struct.unpack_from('<IIII',data,32+i*16);assert k<=5 and aux==0
 if k==2:assert a<1024
 if k>=3:assert a<i and b<i
wrapper=data[:24]+struct.pack('<Q',512)+data[32:32+n*16]+struct.pack('<512I',*([root]*512))
assert wrapper[:24]==data[:24] and wrapper[32:32+n*16]==data[32:32+n*16]
assert struct.unpack_from('<512I',wrapper,32+n*16)==(root,)*512
assert len(wrapper)==32+n*16+512*4
out=d/'guard512.bin';assert not out.exists();out.write_bytes(wrapper)
report={'status':'EXACT_SHARED_NODE_BODY_AND_REPEATED_ROOT_WRAPPER_THEOREM_PASS','original_guard_sha256':sha(data),'wrapper_sha256':sha(wrapper),'unchanged_node_body_sha256':sha(data[32:32+n*16]),'nodes':n,'ports':np,'original_roots':1,'wrapper_roots':512,'root':root,'theorem':'For every1024-bit input assignment and every wrapper output index0..511, output equals original raw G. Header n/np and every node byte are identical; only nr and repeated root table differ. No arithmetic, MR or sampled invariance assumption.','new_mask_or_search_authority':False}
(d/'WRAPPER-EQUIVALENCE.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report))
