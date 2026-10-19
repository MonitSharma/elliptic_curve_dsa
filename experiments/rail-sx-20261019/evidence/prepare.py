import difflib,hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'rail-masks-20261016'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert sha(old/'librail8_masks.so')=='046dd5f1d11386550ec5234b955f6bc1974431e79a6b80499bda97da0ade3e90'
source=(old/'rail8_masks.c').read_text();start=source.index('static inline I sx(');end=source.index('\nstatic inline unsigned window_low',start)
original=source[start:end];assert original.count('width_masks[w]')==5 and '\n' not in original
replacement=(r/'sx.c').read_text().rstrip();new=source[:start]+replacement+source[end:]
probe=(r/'probe.c').read_text()
(r/'baseline.c').write_text(source+'\n'+probe);(r/'specialized.c').write_text(new+'\n'+probe)
shutil.copy2(old/'rail8.h',r/'rail8.h')
(r/'kernel.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),new.splitlines(True),fromfile='frozen/rail8_masks.c',tofile='research/specialized.c')))
(r/'PREPARATION.json').write_text(json.dumps({'status':'ONLY_EXACT_SIGN_EXTENSION_HELPER_CHANGED','original_kernel_sha256':sha(old/'rail8_masks.c'),'original_library_sha256':sha(old/'librail8_masks.so'),'baseline_copy_sha256':sha(r/'baseline.c'),'specialized_copy_sha256':sha(r/'specialized.c'),'unchanged_prefix':source[:start]==new[:start],'unchanged_suffix':source[end:]==new[start+len(replacement):],'advisory_only':True,'active_runtime_modified':False,'nonce_search_enabled':False},indent=2)+'\n')
