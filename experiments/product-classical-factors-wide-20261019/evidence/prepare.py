"""Research-only larger support. Frozen classical9 source remains untouched."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'product-classical-factors-refresh-20261019';p=r/'proof';p.mkdir(exist_ok=False)
for name in ['mod.rs','affine_simplify.rs','quadratic_simplify.rs','classical_factors_xor.rs','product7_simplify.rs','tests_classical_factors.rs']:shutil.copy2(old/'proof'/name,p/name)
for name in ['io.rs','refresh_factors.rs','factor_trace.rs']:shutil.copy2(old/name,r/name)
s=(p/'classical_factors_xor.rs').read_text();s=s.replace('const SUPPORT_CAP: usize = 7;','const SUPPORT_CAP: usize = 9;').replace('table: u128,','table: Table,')
first=s.index('impl Truth {');last=s.index('\nstruct Support {',first);s=s[:first]+'include!("../table.rs");\n'+s[last:]
assert s.count('table: 2,')==1;s=s.replace('table: 2,','table: Table::low(2),')
assert s.count('if atoms.len() > SUPPORT_CAP {')==1;s=s.replace('if atoms.len() > SUPPORT_CAP {','if atoms.len() > support_cap() {')
assert s.count('let mut table = 0;')==1;s=s.replace('let mut table = 0;','let mut table = Table::low(0);')
assert s.count('table |= value << row;')==1;s=s.replace('table |= value << row;','table.set(row, value);')
s+='\n#[cfg(test)] #[path="../tests_table.rs"] mod wide_table_tests;\n';(p/'classical_factors_xor.rs').write_text(s)
s=(p/'product7_simplify.rs').read_text();s=s.replace('use super::{Rewrite, Support, Truth, SUPPORT_CAP};','use super::{Rewrite, Support, Truth, Table, support_cap};').replace('if atoms.len() > SUPPORT_CAP {','if atoms.len() > support_cap() {').replace('let mut table = 0;','let mut table = Table::low(0);').replace('table |= (a.value_in_union(&left, row) & b.value_in_union(&right, row)) << row;','table.set(row, a.value_in_union(&left, row) & b.value_in_union(&right, row));');(p/'product7_simplify.rs').write_text(s)
files={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/'proof').rglob('*') if p.is_file()}
(r/'PREPARATION.json').write_text(json.dumps({'status':'RESEARCH_ONLY_FIXED_512_BIT_TRUTH_TABLE_PORT','source_files':files,'input_cases':['cap7 parent4 must reproduce exact previously controlled simple8','cap9 frozen classical9 source; only genuinely additional executed saving matters'],'frozen_candidate_changed':False},indent=2)+'\n')
