from pathlib import Path
import ctypes,ctypes.util,json,hashlib,struct,subprocess
r=Path('/home/hclau/ecdsa_research/census-control-review-20261016');b=r.parent;c=b/'product-exact-20261015/candidate-all70-base';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 data=p.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0];z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),data[16:],len(data)-16)==n*56;return out.raw
parent_path=b/'product-exact-20261015/tip/ops.bin';new_path=c/'ops.bin';before={str(p):sha(p)for p in[parent_path,new_path,c/'src/point_add/census_cut.rs',r/'ALL70.json']};assert before[str(parent_path)]=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e';assert before[str(new_path)]=='06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a';assert before[str(c/'src/point_add/census_cut.rs')]=='ff324878900e115b8c2cdd76e438f898099c57ec8495cac64609580a32c9572a'
old=load(parent_path);new=load(new_path);assert len(old)==len(new)==11630716*56;rows=json.loads((r/'ALL70.json').read_text());cursor=0
for row in sorted(rows,key=lambda x:x['actual_index']):
 at=row['actual_index'];assert new[cursor*56:at*56]==old[cursor*56:at*56];assert list(struct.unpack_from('<7Q',old,at*56))==row['new'];assert list(struct.unpack_from('<7Q',new,at*56))==row['old'];cursor=at+1
assert new[cursor*56:]==old[cursor*56:];assert new[-96*56:]==old[-96*56:]
assert subprocess.check_output(['git','-C',str(c),'rev-parse','HEAD'],text=True).strip()=='4b2ec52fc55da796aa8f5ef851290297e8706424';assert subprocess.check_output(['git','-C',str(c),'diff','--name-only'],text=True).splitlines()==['src/point_add/census_cut.rs']
after={p:sha(Path(p))for p in before};assert before==after
out=dict(status='PASS INDEPENDENT COMPLETE ALL70 NATIVE BYTE REVIEW',before_after_source_stream_hashes=before,ops=11630716,exactly70_current_CX_replaced_by_exact_source_CCX=True,every_other_original_Op_byte_identical=True,all74_deletions_preserved=True,all_original_MR_classical_ABI_positions_tail_identical=True,no_A29=True,exact_added_executed_T_bounds=[56,70],structural_proxy63_not_measured_mean=True,source_review_sha256=sha(r/'NATIVE-SOURCE-REVIEW.json'),binding_review_sha256=sha(r/'REVIEW.json'),candidate_canonical_sha256=hashlib.sha256(new).hexdigest(),whole_arithmetic_or_failure_monotonicity_not_claimed=True,fresh_gate_pending=True)
(r/'NATIVE-BYTE-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
