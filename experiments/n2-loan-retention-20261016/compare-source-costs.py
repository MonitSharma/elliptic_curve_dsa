from pathlib import Path
import json,struct,ctypes,ctypes.util,re,hashlib
r=Path('/home/hclau/ecdsa_research/n2-loan-retention-20261016');a=r.parent/'current-value-attribution-20261016'
assert(a/'phase-attribution.exit').read_text().strip()=='0','serialize after owned1core replay'
assert(r/'all-retained-generation.exit').read_text().strip()=='101';assert(r/'all-retained-cap8-generation.exit').read_text().strip()=='101'
p=a/'raw-builder.bin';d=p.read_bytes();assert hashlib.sha256(d).hexdigest()=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69';n=struct.unpack_from('<Q',d,8)[0]
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;raw=o.raw
markers=json.loads((a/'actual-loan-markers.json').read_text())['markers'];bound={x['raw_at']:(x['phase'],x['label'])for x in markers};costs={};t=0.;depth=0;ccx=0;mr=0
for i in range(n):
 if i in bound:assert depth==0;costs[bound[i]]=t
 k=struct.unpack_from('<Q',raw,i*56)[0]
 if k==15:depth+=1
 elif k==16:depth-=1;assert depth>=0
 elif k in[13,14]:t+=2.**(-depth);ccx+=1
 elif k in[11,12]:mr+=1
assert depth==0
text=(r/'all-retained-cap8-generation.log').read_text();new={m[1]:float(m[2])for m in re.finditer(r'N2_RETENTION_END phase=(\w+) .*?source_expected_T_delta=([\d.]+)',text)}
rawnew=float(re.search(r'N2_RETENTION_RAW_COMPLETE .*?source_expected_T=([\d.]+)',text)[1]);components=[]
for phase in ['divide','multiply']:
 old=costs[phase,'in-after']-costs[phase,'out-before'];components.append(dict(phase=phase,original_raw_expected_T=old,retained_scoped8_raw_expected_T=new[phase],delta_expected_T=new[phase]-old))
out=dict(status='TERMINAL SOURCE-ONLY RESOURCE AUDIT; NO NATIVE CANDIDATE OR SAMPLING',family='ALL N2 rail loans disabled, all original rail bits retained',base_source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',base_actual_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',base_raw_stream_sha256=hashlib.sha256(d).hexdigest(),
 at_original_Q=dict(cap=1234,result='FAIL source capacity at first forwardN2 bodyt131',exact_reason='fold short28(room8,need36); m0erase short18(room13,need31); shed block14 +tops2 +fin4; no completed stream'),
 scoped_extra8=dict(cap=1242,peak_and_physical_Q=1242,source_raw_ops=int(re.search(r'N2_RETENTION_RAW_COMPLETE ops=(\d+)',text)[1]),original_raw_ops=n,original_raw_expected_T=t,retained_raw_expected_T=rawnew,raw_delta_expected_T=rawnew-t,
 source_expected_definition='same Builder model: every CCX/CCZ weighted2^-PushDepth; source component only, not scored or fully optimized',components=components,
 native_result='FAIL preserved rebind y42_bound region489932Ops found0times; no bypass and no ops.bin/census',extra_capacity_scope='entire source n2_div_batch and n2_mul_batch, including their rail preludes; no minimal-capacity claim'),
 no_remaining_N2_clean_loan_assumptions=True,no_unconditional_reset_or_discard=True,no_global_arithmetic_correctness_claim=True,no_fresh_sampling=True,
 provenance_limit='Scoped width changes source layout/physicalABI/stream before protected bound tables, so raw T comparisons cannot be promoted to a scored circuit. Candidate inputs/nonce packets never used.')
(r/'SOURCE-COST-RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
