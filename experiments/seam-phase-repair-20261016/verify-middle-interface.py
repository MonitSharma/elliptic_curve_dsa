exec((__import__('pathlib').Path(__file__).parent/'prepare-region.py').read_text().split('oldwhole=')[0])
import collections
# The first full-word X layer complements x; the second restores D after the
# exact classical-addend ripple. Everything through that second layer is exact.
sub_end=None
for i in range(begin+256,site-255):
 if all(R[i+j]==(6,none,none,j,none,none,none)for j in range(256)):
  sub_end=i+256;break
assert sub_end is not None
prefix=raw[begin*56:sub_end*56];fa=final.find(prefix);assert fa>=0 and fa%56==0 and final.find(prefix,fa+1)<0
component=raw[site*56:end*56];fc=final.find(component);assert fc>=0 and fc%56==0 and final.find(component,fc+1)<0
actual_begin=fa//56;actual_sub_end=actual_begin+sub_end-begin;actual_hmr=fc//56;middle=list(struct.iter_unpack('<7Q',final[actual_sub_end*56:actual_hmr*56]));writes=collections.defaultdict(list);depth=0
for i,o in enumerate(middle):
 k,b,a,t,bt,bc,reg=o
 if k in[6,8,10,11,12,13]:
  for q in[t]+([a]if k==10 else[]):
   if q==target or lowq<=q<256:writes[q].append(dict(at=actual_sub_end+i,row=o,depth=depth))
 if k==15:depth+=1
 if k==16:depth-=1
assert depth==0
assert not writes[lowq]
for q in u:
 assert len(writes[q])==1 and writes[q][0]['row']==(6,none,none,q,none,none,none)and writes[q][0]['depth']==0
assert len(writes[target])%2==0 and all(w['row']==(6,none,none,target,none,none,none)and w['depth']==0 for w in writes[target])
assert all(not(o[0]in[3,4,5,12]and o[4]<256)for o in struct.iter_unpack('<7Q',final))
nq=1234;nb=45701;lib=ctypes.CDLL(str(r.parent/'precision-family-20261016/constant_zero.so'));lib.constant_zeros.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t),ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p];lib.constant_zeros.restype=ctypes.c_int
iq=(ctypes.c_int8*nq)();ib=(ctypes.c_int8*nb)()
for i in range(512):iq[i]=-1;ib[i]=-1
query=(ctypes.c_size_t*1)(actual_begin);zeros=ctypes.create_string_buffer(nq);assert lib.constant_zeros(final,actual_begin+1,nq,nb,query,1,zeros,iq,ib)==0
scratch=sorted({q for o in R[begin:sub_end]for q in o[1:4]if q!=none and q>=512});assert all(zeros.raw[q]for q in scratch)
result=dict(status='SOURCE_PREFIX_AND_ACTUAL_MIDDLE_INTERFACE_PROVED',actual_begin=actual_begin,actual_subtraction_end=actual_sub_end,actual_hmr=actual_hmr,raw_subtraction_end=sub_end,exact_source_subtraction_prefix_byteidentical=True,prefix_scratch_provedzero_for_all_input_MR=scratch,lower_q_untouched_through_inherited_middle=lowq,upper_q_one_unconditional_X_each=u,ov_unconditional_X_parity_even=len(writes[target]),ov_other_quantum_writes=0,classical_ox_immutable_all_stream=True,all_existing_lowfold_edits_retained=True,middle_writes=dict(writes),actual_middle_sha256=hashlib.sha256(final[actual_sub_end*56:actual_hmr*56]).hexdigest())
(r/'source-middle-interface.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='middle_writes'},indent=2))
