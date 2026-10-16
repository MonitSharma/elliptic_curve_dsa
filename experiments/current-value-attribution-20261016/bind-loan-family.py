from pathlib import Path
import json,hashlib,struct,ctypes,ctypes.util,collections
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016')
assert(r/'loan-markers.exit').read_text().strip()=='0'
assert(r/'raw-loan-builder.sha256').read_text().split()[0]=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69'
s=(r/'map-final-markers.py').read_text().replace("'raw-markers.jsonl'","'raw-loan-markers.jsonl'").replace("'actual-markers.json'","'actual-loan-markers.json'")
(r/'map-loan-markers.py').write_text(s)
exec(compile(s,str(r/'map-loan-markers.py'),'exec'))
bound=json.loads((r/'actual-loan-markers.json').read_text());assert bound['unknown_regions']==0 and bound['admitted_markers']==8
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
d=(r.parent/'product-exact-20261015/tip/ops.bin').read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;raw=o.raw
def op(i):return struct.unpack_from('<7Q',raw,i*56)
families=[]
for phase in ['divide','multiply']:
 ms={m['label']:m for m in bound['markers']if m['phase']==phase};assert len(ms)==4
 start,end=ms['out-before']['at'],ms['out-after']['at'];stop,after=ms['in-before']['at'],ms['in-after']['at'];assert end-start==8 and after-stop==8
 rails=[ms['out-before']['rail0'],ms['out-before']['rail1']];assert all(len(x)==5 for x in rails)
 lent=[q for rail in rails for q in rail[:4]];expected=[(rail[-1],q)for rail in rails for q in rail[:4]]
 assert all(op(at)==(8,2**64-1,sg,q,2**64-1,2**64-1,2**64-1)for at,(sg,q)in zip(range(start,end),expected))
 touches=collections.defaultdict(list);all_touched=set()
 for at in range(end,stop):
  row=op(at)
  if row[0] in [0,3,4,5,15,16,17]:continue
  for q in set(row[1:4]):
   if q!=2**64-1:all_touched.add(q)
   if q in lent:touches[q].append((at,row))
 stats=[]
 for q in lent:
  t=touches[q];mrs=[(at,row)for at,row in t if row[0]in[11,12]and row[3]==q]
  stats.append(dict(q=q,first_touch=t[0]if t else None,first_MR=mrs[0]if mrs else None,touches=len(t),MRs=len(mrs)))
 families.append(dict(phase=phase,out_span=[start,end],returned_span=[stop,after],whole_borrow_interval=[start,after],source_rails_bit1through5=rails,lent_q=stats,
  all_untouched_q_between_out_and_in=[q for q in range(1234)if q not in all_touched],
  exact_loan_premise='all four low rail bits equal bit5/sign; with implicit odd bit0 this is exactly signed6bit rail==+1 or-1',
  no_repair_or_closure_claim=True))
out=dict(status='ALL SOURCE n2_loan_out /n2_loan_in sites bound',source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',actual_stream_sha256=hashlib.sha256(d).hexdigest(),source_call_sites=2,source_rail_loans=4,source_loan_release_clean_calls=16,
 metadata_source_file_sha256=hashlib.sha256((r/'source-loan-observer/src/point_add/leapfrog.rs').read_bytes()).hexdigest(),source_raw_stream_unchanged=True,all_markers_unique_actual_literal_bindings=True,families=families)
(r/'n2-loan-family.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
