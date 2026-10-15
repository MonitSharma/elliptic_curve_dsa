from pathlib import Path
import os,hashlib,json,datetime
r=Path(__file__).resolve().parent;rows=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  if Path(os.readlink(p/'exe'))!=r/'tool/target/release/value_prefilter':continue
  env=dict(x.split(b'=',1)for x in(p/'environ').read_bytes().split(b'\0')if b'='in x)
  keys=['SCALAR_FAST_LIB','FAST_ZERO_DISPATCH','FUSED_GUARD','FUSED_GUARD_SHADOW','FORCE_FULL_FALLBACK','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW']
  selected={key:env.get(key.encode(),b'').decode()for key in keys}
  libraries=sorted({line.split()[-1]for line in(p/'maps').read_text().splitlines()if'/home/hclau/ecdsa_research/'in line and'.so'in line})
  scalar='/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so'
  if scalar not in libraries:continue
  hashes={path:hashlib.sha256(Path(path).read_bytes()).hexdigest()for path in libraries}
  assert not selected['SCALAR_FAST_LIB'] and hashes[scalar]=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
  rows.append({'pid':int(p.name),'selected_nonsecret_environment':selected,'mapped_research_library_sha256':hashes,'actual_scalar_library_verified':True})
 except(FileNotFoundError,ProcessLookupError,PermissionError):continue
assert rows,'No initialized isolated runtime to capture; do not infer a binding'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
out=r/f'ACTUAL_RUNTIME_BINDINGS-{stamp}.json'
out.write_bytes((json.dumps({'status':'ISOLATED_ACTUAL_SCALAR_AND_RESEARCH_LIBRARY_BINDINGS_CAPTURED','rows':rows},indent=2)+'\n').encode());print(out)
