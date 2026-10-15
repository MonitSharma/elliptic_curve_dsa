"""Read only selected provenance fields; never dump the process environment."""
from pathlib import Path
import datetime,hashlib,json,os
root=Path(__file__).resolve().parent
rows=[]
for entry in Path('/proc').iterdir():
    if not entry.name.isdigit():continue
    try:
        exe=Path(os.readlink(entry/'exe'))
        if exe!=root/'tool/target/release/value_prefilter':continue
        env=dict(part.split(b'=',1) for part in (entry/'environ').read_bytes().split(b'\0') if b'=' in part)
        selected={name:env.get(name.encode(),b'').decode() for name in ['SCALAR_FAST_LIB','FAST_ZERO_DISPATCH','FORCE_FULL_FALLBACK','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW']}
        libraries=sorted({line.split()[-1] for line in (entry/'maps').read_text().splitlines() if '/home/hclau/ecdsa_research/' in line and '.so' in line})
        hashes={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in libraries}
        scalar=selected['SCALAR_FAST_LIB'] or '/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so'
        assert scalar in hashes and hashes[scalar]=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
        rows.append(dict(pid=int(entry.name),selected_nonsecret_environment=selected,mapped_research_libraries_sha256=hashes,scalar_binding_verified=True))
    except (FileNotFoundError,ProcessLookupError,PermissionError):continue
assert rows,'no active isolated validation process to observe'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
out=root/f'actual-runtime-bindings-{stamp}.json'
out.write_text(json.dumps({'status':'ACTUAL_PROCESS_SELECTED_ENVIRONMENT_AND_MAPPED_LIBRARY_HASHES_RECORDED','rows':rows,'no_full_environment_readout':True},indent=2)+'\n')
print(str(out))
