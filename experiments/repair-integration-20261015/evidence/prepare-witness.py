"""Read a nonzero path from the existing BDD; leave all audit algebra intact."""
from pathlib import Path
import shutil,json,hashlib
root=Path(__file__).resolve().parent;dest=root/'phase-bdd-witness';assert not dest.exists();shutil.copytree(root/'phase-bdd',dest)
p=dest/'src/phase_kernel.rs';parent=p.read_bytes();assert hashlib.sha256(parent).hexdigest()=='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
addition=r'''
/// Inspect the retained final graph after a nonzero-phase result. Omitted
/// variables are zero. No graph or simulation state is changed.
pub fn nonzero_witness(root:u32)->(Vec<usize>,u64) {
    assert_ne!(root,0);
    GRAPH.with(|g|{let m=g.borrow();let mut at=root;let mut ones=Vec::new();
        loop {let n=m.nodes[at as usize];
            if n.var==u32::MAX {assert_ne!(n.value,0);return (ones,n.value);}
            if n.low!=0 {at=n.low;} else {ones.push(n.var as usize);at=n.high;}
        }
    })
}
#[cfg(test)]
mod witness_tests {
 use super::*;
 #[test]
 fn witness_paths_match_exact_truth_tables_and_gc() {
  reset_manager();let x=Poly::variable(0).unwrap();let y=Poly::variable(1).unwrap();let z=Poly::variable(2).unwrap();
  let expressions=[x,x.xor(&y).unwrap(),x.and(&y).unwrap(),x.not().unwrap().and(&z).unwrap(),x.and(&Poly::constant(0x12345678)).unwrap().xor(&y.and(&Poly::constant(0xff00ff)).unwrap()).unwrap()];
  for f in expressions {let(ones,mask)=nonzero_witness(f.0);let actual=GRAPH.with(|g|{let m=g.borrow();let mut at=f.0;loop{let n=m.nodes[at as usize];if n.var==u32::MAX{break n.value;}at=if ones.contains(&(n.var as usize)){n.high}else{n.low};}});assert_eq!(mask,actual);assert_ne!(mask,0);}
  let f=expressions[4];GRAPH.with(|g|g.borrow_mut().collect(&[f.0]));let(ones,mask)=nonzero_witness(f.0);let wanted=if ones.contains(&0){0x12345678}else{0} ^ if ones.contains(&1){0xff00ff}else{0};assert_eq!(mask,wanted);reset_manager();
 }
}
'''
p.write_bytes(parent+addition.encode())
p=dest/'src/main.rs';s=p.read_text();start=s.index('   if let Some(t)=e.split(');end=s.index('\n  }\n }\n let mut phases',start)
s=s[:start]+'''   if e.starts_with("nonzero phase polynomial represented by exact decision diagram:") {
    let root:u32=e.split("root=").nth(1).unwrap().split_whitespace().next().unwrap().parse().unwrap();
    let (ones,mask)=phase_kernel::nonzero_witness(root);selected=ones;expected_coefficient=Some(mask);
    println!("BDD_WITNESS selected_count={} expected_phase={mask:#x} selected={selected:?}",selected.len());
    for &mr in selected.iter().take(20) {let at=map[mr];println!("PHASE_ORIGIN measurement={mr} op={at}");for i in at.saturating_sub(12)..(at+20).min(ops.len()){println!("PHASE_NEIGHBOR op={i} gate={:?}",ops[i]);}}
   }'''+s[end:]
needle=' if selected.len()==1 {';assert s.count(needle)==1;s=s.replace(needle,' if let Some(mask)=expected_coefficient {assert_eq!(phases[1],mask);assert_ne!(phases[0],phases[1]);println!("BDD_NATIVE_COUNTEREXAMPLE_VERIFIED=true");}\n'+needle);p.write_text(s)
(root/'witness-manifest.json').write_text(json.dumps({'score':None,'scope':'Read-only nonzero-path extraction appended to unchanged BDD audit; validate resulting assignment in protected native simulator. Same first fixed zero-slope input.','kernel_parent_sha256':hashlib.sha256(parent).hexdigest(),'sources':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}},indent=2)+'\n')
