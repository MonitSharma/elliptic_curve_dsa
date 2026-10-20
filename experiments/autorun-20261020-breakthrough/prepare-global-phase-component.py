from pathlib import Path
import hashlib, json, shutil

a = Path(__file__).parent
ex = a.parent
old = ex / 'breakthrough-global-prefix-component-v4-20261020'
r = ex / 'breakthrough-global-phase-component-20261020'
r.mkdir(exist_ok=False)
t = r / 'local-tool'
t.mkdir()
for n in ['Cargo.toml', 'Cargo.lock', 'io.rs']:
    shutil.copyfile(old / 'local-tool' / n, t / n)
s = (a / 'global-prefix-simplify-v4.rs').read_text()
start = s.index('}else if o.kind==K::CCZ{')
end = s.index('\n  if !done{', start)
s = s[:start] + r''' }else if o.kind==K::CCZ{
   let ab=alg.and(&q[a],&q[b]);let value=alg.and(&ab,&q[t]);let phase=alg.and(&eff,&value);
   if phase.is_empty(){*counts.entry("zero_ccz").or_default()+=1;done=true;}
   else if phase==eff{out.push(make(K::Neg,no,no,no,no,o.c_condition.0));*counts.entry("ccz_to_neg").or_default()+=1;done=true;}
   else{
    for wire in[a,b,t]{let v=alg.and(&eff,&q[wire]);if phase==v{out.push(make(K::Z,no,no,wire as u64,no,o.c_condition.0));*counts.entry("ccz_to_z").or_default()+=1;done=true;break;}}
    if !done{for(x,y)in[(a,b),(a,t),(b,t)]{let xy=alg.and(&q[x],&q[y]);let v=alg.and(&eff,&xy);if phase==v{out.push(make(K::CZ,no,x as u64,y as u64,no,o.c_condition.0));*counts.entry("ccz_to_cz").or_default()+=1;done=true;break;}}}
    if !done{let mut found=None;for(control,x,y)in[(a,b,t),(b,a,t),(t,a,b)]{if let Some(bits)=index.get(&q[control]){if let Some(&bit)=bits.first(){found=Some((bit,x,y,false));break;}}let complement=Algebra::xor_raw(&q[control],&one);if let Some(bits)=index.get(&complement){if let Some(&bit)=bits.first(){found=Some((bit,x,y,true));break;}}}if let Some((bit,x,y,negative))=found{if negative{out.push(make(K::CZ,no,x as u64,y as u64,no,o.c_condition.0));}out.push(make(K::PushCondition,no,no,no,no,bit as u64));out.push(make(K::CZ,no,x as u64,y as u64,no,o.c_condition.0));out.push(make(K::PopCondition,no,no,no,no,no));*counts.entry(if negative{"ccz_classical_complement"}else{"ccz_classical_alias"}).or_default()+=1;done=true;}}
   }
  }''' + s[end:]
pos = s.rfind('\n}')
s = s[:pos] + r'''
 #[test]fn phase_lowerings_keep_absolute_phase_and_all_original_guards(){let n=u64::MAX;
  let mut ops=metadata();ops.extend([make(K::X,n,n,4,n,n),make(K::X,n,n,5,n,n),make(K::PushCondition,n,n,n,n,0),make(K::CCZ,4,5,0,n,1),make(K::PopCondition,n,n,n,n,n)]);let(out,s)=global_prefix_simplify(&ops,1024);assert_eq!(s["rewrites"]["ccz_to_z"],1);compare(&ops,&out,None);
  let mut ops=metadata();ops.extend([make(K::X,n,n,4,n,n),make(K::CCZ,0,4,1,n,1)]);let(out,s)=global_prefix_simplify(&ops,1024);assert_eq!(s["rewrites"]["ccz_to_cz"],1);compare(&ops,&out,None);
  let mut ops=metadata();ops.extend([make(K::X,n,n,4,n,n),make(K::X,n,n,5,n,n),make(K::CCZ,4,5,4,n,1)]);let(out,s)=global_prefix_simplify(&ops,1024);assert_eq!(s["rewrites"]["ccz_to_neg"],1);let bad:Vec<_>=out.iter().filter(|o|o.kind!=K::Neg).copied().collect();compare(&ops,&out,Some(&bad));
 }
 #[test]fn phase_product_relation_can_remove_one_t_without_sampling(){let n=u64::MAX;let mut ops=metadata();ops.extend([make(K::CCX,0,1,4,n,n),make(K::CCZ,0,1,4,n,0)]);let(out,s)=global_prefix_simplify(&ops,1024);assert_eq!(s["rewrites"]["ccz_to_cz"],1);compare(&ops,&out,None);}
 #[test]fn phase_classical_alias_complement_and_mutation_preserve_rng_and_phase(){let n=u64::MAX;for target in[0,1,4]{for mutate in[false,true]{let mut ops=metadata();ops.extend([make(K::Hmr,n,n,5,2,n),make(K::X,n,n,4,n,2)]);if mutate{ops.push(make(K::BitInvert,n,n,n,2,n));}ops.push(match target{0=>make(K::CCZ,4,0,1,n,0),1=>make(K::CCZ,0,4,1,n,0),_=>make(K::CCZ,0,1,4,n,0)});let(out,s)=global_prefix_simplify(&ops,1024);assert_eq!(s["rewrites"][if mutate{"ccz_classical_complement"}else{"ccz_classical_alias"}],1);compare(&ops,&out,None);}}}
 #[test]fn independent_registered_phase_controls_are_not_lowered(){let n=u64::MAX;let mut ops=metadata();ops.extend([make(K::CCZ,0,1,2,n,n),make(K::CCZ,0,1,2,n,0)]);let(out,s)=global_prefix_simplify(&ops,1024);assert!(s["rewrites"].as_object().unwrap().is_empty());assert_eq!(hash(&ops),hash(&out));compare(&ops,&out,None);}
''' + s[pos:]
(r / 'global-phase-simplify.rs').write_text(s)
original = (old / 'local-tool/discover.rs').read_text()
gs = original.index('// Full-prefix exact Boolean replay.')
main = original.index('\nfn main(){', gs)
(t / 'discover.rs').write_text(original[:gs] + s + original[main:])
sha = lambda p: hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
f = json.loads((old / 'SOURCE-FREEZE.json').read_bytes())
f.update(tool_source_files={n: sha(t/n) for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']}, native_controls=18,
    scope='Exact full-prefix phase and action equalities only. Lower CCZ to NEG/Z/CZ or classical-conditioned CZ using full symbolic equality/current classical aliases. Preserve absolute phase, guards, all classical mutations and random draws. Components only, no gate/nonce/benchmark/score.')
(r / 'SOURCE-FREEZE.json').write_text(json.dumps(f, indent=2)+'\n')
for name in ['run.py','run-local.sh']:
    data = (old/name).read_text().replace(old.name,r.name).replace('native_controls\':14','native_controls\':18').replace('14 passed; 0 failed;','18 passed; 0 failed;')
    (r/name).write_bytes(data.encode())
(r / '.gitignore').write_text('local-tool/\n__pycache__/\n*.ops.bin\n')
(r / '.gitattributes').write_text('* -text\n')
(r / 'PLAN.md').write_text('''# Exact phase reductions on current product and Toffoli parents

Extend the native14-qualified full-prefix simplifier with four exhaustive phase
controls: absolute NEG retained, single/pair lowering, proven product relation,
all three positions of classical aliases/complements under mutated classical
bits, and independent-control negative control. All original protected phase,
guards and random words must match. Source and both original input streams
frozen before running; no packet information used in rewriting.

Fixed cap1024/product memo65536, local5GiB/900s per source. Component diagnostics
only. Any useful circuit must be bound into point_add source and pass its own
development/final gate/ascending nonce/unchanged benchmark before submission.
''')
print(r.name)
