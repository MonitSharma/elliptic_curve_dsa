import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'product-classical-factors-wide-20261019/evidence';p=r/'proof';p.mkdir(exist_ok=False)
for name in ['mod.rs','affine_simplify.rs','quadratic_simplify.rs','classical_factors_xor.rs','product7_simplify.rs','tests_classical_factors.rs']:
    shutil.copy2(old/'proof'/name,p/name)
for name in ['io.rs','refresh_factors.rs','factor_trace.rs']:shutil.copy2(old/name,r/name)
s=(p/'classical_factors_xor.rs').read_text().replace('const SUPPORT_CAP: usize = 9;','const SUPPORT_CAP: usize = 11;');(p/'classical_factors_xor.rs').write_text(s,newline='\n')
s=(old/'table.rs').read_text().replace('512','2048').replace('[u64;8]','[u64;32]').replace('[0;8]','[0;32]').replace('count<=9','count<=11').replace('|_|"9"','|_|"11"').replace('[7,9]','[9,11]');(r/'table.rs').write_text(s,newline='\n')
assert 'row<2048' in s and 'struct Table([u64;32]);' in s
files={q.relative_to(r).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in [*p.glob('*.rs'),r/'table.rs',r/'io.rs',r/'refresh_factors.rs',r/'factor_trace.rs',r/'tests_table.rs']}
(r/'PREPARATION.json').write_text(json.dumps({'status':'LOCAL_RESEARCH_EXACT_2048_ROW_TABLE_PREPARED','files':files,'new_candidate_source_changed':False,'live_server_jobs_changed':False},indent=2)+'\n')
