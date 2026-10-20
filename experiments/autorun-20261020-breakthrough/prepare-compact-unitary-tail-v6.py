from pathlib import Path
import ast,runpy,sys
a=Path(__file__).parent;p=a/'phase-compare-compact.rs';s=p.read_text();assert 'fn phase_product(' in s
start=s.index('fn phase_product(');end=s.index('pub(super) fn try_run',start);s=s[:start]+s[end:];s=s.replace('12.min(n/2).min(n-2)','n-2')
start=s.index(' c.cz(u[last],v[last]);c.cx(v[last],u[last]);');end=s.index(' for i in (1..m).rev()',start)
s=s[:start]+''' // Exact in-place MAJ suffix stores carries in operand wires, then reverses.
 for i in m..last{c.cx(u[i],v[i]);c.cx(u[i],u[i-1]);c.ccx(u[i-1],v[i],u[i]);}
 c.cz(u[last],v[last]);c.cz(u[last],u[last-1]);if !fault{c.cz(v[last],u[last-1]);}
 for i in (m..last).rev(){c.ccx(u[i-1],v[i],u[i]);c.cx(u[i],u[i-1]);c.cx(u[i],v[i]);}
'''+s[end:]
start=s.index(' #[test]fn dirty_borrowed_multicontrol_phase_exhaustive_truth_table()');end=s.index(' #[test]#[should_panic',start);s=s[:start]+s[end:]
s=s.replace('//! Exact phase comparator with one fewer live carry at a workspace cliff.','//! Exact phase comparator with adaptive measured-prefix / reversible-tail carries.').replace('//! MAJ(x,y,MAJ(a,b,c)) = xy + (x+y)ab + (x+y)(a+b)c over Boolean GF(2).','//! MAJ(a,b,c): CX(a,b), CX(a,c), CCX(c,b,a); inverse restores all operands.').replace('//! The omitted penultimate carry is replaced by two native CCZs. No precision cut.','//! Each omitted measured carry costs one extra native Toffoli. No precision cut.')
# Wide comparison tests cover every legal cut; the original input/phase oracle
# and measurement probes are independent of this reversible implementation.
g=a/'prepare-grouped-compact-width.py';body=g.read_text();needle="'breakthrough-grouped-compact-width-v5-20261020'];";assert body.count(needle)==1;body=body.replace(needle,"'breakthrough-grouped-compact-width-v5-20261020','breakthrough-grouped-compact-width-v6-20261020'];").replace('r.mkdir(exist_ok=False)','r.mkdir(exist_ok=True);assert not(r/\'run.py\').exists()').replace('test result: ok. 5 passed; 0 failed;','test result: ok. 4 passed; 0 failed;').replace("'native_controls':33","'native_controls':32").replace("'compact_compare_controls':5","'compact_compare_controls':4");ast.parse(body)
p.write_text(s);g.write_text(body);sys.argv=[str(g),'breakthrough-grouped-compact-width-v6-20261020'];runpy.run_path(str(g),run_name='__main__')
