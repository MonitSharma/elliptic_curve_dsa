from pathlib import Path
r=Path(__file__).resolve().parent;e=r.parent
s=(e/'product-schedule-20261019/borrow.rs').read_text(encoding='utf-8')
s=s[:s.index('fn rewrite(')]
# Read-only query support is validated separately; writes still prohibit reuse.
s=s.replace('for q in qubits(o){last[q as usize]=Some(i);}', '''if matches!(o.kind,K::X|K::CX|K::CCX|K::R|K::Hmr|K::Swap){if o.q_target.0!=NO{last[o.q_target.0 as usize]=Some(i);}if o.kind==K::Swap&&o.q_control1.0!=NO{last[o.q_control1.0 as usize]=Some(i);}}''')
s=s.replace('let pinned:HashSet<_>','let pinned_b:HashSet<_>=v.iter().filter(|o|o.kind==K::AppendToRegister&&o.c_target.0!=NO).map(|o|o.c_target.0).collect();\n let pinned:HashSet<_>')
s=s.replace('&&hmr_safe.contains(&(i+s.measurement_offset()))','&&hmr_safe.contains(&(i+s.measurement_offset()))&&!pinned_b.contains(&bit)')
start=s.index(' // Composition uses nested or disjoint scopes;')
end=s.index('\nfn gate(',start)
s=s[:start]+' found\n}\n'+s[end:]
(r/'detector.rs').write_text(s.replace('//!','//',1),encoding='utf-8',newline='\n')
for name in ('io.rs','preflight.py'):(r/name).write_bytes((e/'product-guard-lifetimes-20261019'/name).read_bytes())
print('Prepared write-epoch detector; query decoder and controls appended separately')
