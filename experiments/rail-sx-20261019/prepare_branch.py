import difflib,hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'rail-masks-20261016'
assert (r/'run.exit').read_text().strip()=='0'
result=json.loads((r/'RESULT.json').read_text());assert result['status']=='EXACT_SX_AND_ADVISORY_FLAGS_VERIFIED'
source=(old/'rail8_masks.c').read_text();start=source.index('static inline I sx(');end=source.index('\nstatic inline unsigned window_low',start)
replacement=(r/'sx_branch.c').read_text().rstrip();new=source[:start]+replacement+source[end:]
(r/'branch.c').write_text(new+'\n'+(r/'probe.c').read_text())
(r/'branch.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),new.splitlines(True),fromfile='frozen/rail8_masks.c',tofile='research/branch.c')))
s=(r/'verify.py').read_text().replace("r/'libspecialized.so'","r/'libbranch.so'").replace("r/'RESULT.json'","r/'RESULT-BRANCH.json'").replace("'EXACT_SX_AND_ADVISORY_FLAGS_VERIFIED'","'EXACT_BRANCH_SX_AND_ADVISORY_FLAGS_VERIFIED'")
(r/'verify_branch.py').write_text(s)
(r/'BRANCH-PREPARATION.json').write_text(json.dumps({'change':'Fixed-limb branches and forced inline avoid dynamic array indexing/spills. Same exact sign extension; all other kernel source unchanged.','v1_preserved':True,'v1_speedup':result['advisory_only_speedup'],'branch_source_sha256':hashlib.sha256((r/'branch.c').read_bytes()).hexdigest(),'active_runtime_changed':False,'nonce_search_enabled':False},indent=2)+'\n')
