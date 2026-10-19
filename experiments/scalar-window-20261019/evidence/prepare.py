import difflib,hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'scalar-fast-20261015'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert sha(old/'libscalar_fast_batch.so')=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
s=(old/'scalar_batch.c').read_text();needle='window<8||window>20||public_fixed_table';assert s.count(needle)==1
new=s.replace(needle,'window<8||window>24||public_fixed_table');(r/'scalar_extended.c').write_text(new)
(r/'source.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),new.splitlines(True),fromfile='frozen/scalar_batch.c',tofile='research/scalar_extended.c')))
(r/'PREPARATION.json').write_text(json.dumps({'status':'ONLY_ACCEPTED_PUBLIC_TABLE_WINDOW_UPPER_BOUND_CHANGED','original_library_sha256':sha(old/'libscalar_fast_batch.so'),'original_source_sha256':sha(old/'scalar_batch.c'),'new_source_sha256':sha(r/'scalar_extended.c'),'windows':[20,22,24],'curve_arithmetic_and_table_algorithm_unchanged':True,'circuit_or_active_runtime_changed':False,'nonce_tested':False},indent=2)+'\n')
