"""Full-stream fixed-input phase polynomial audit using the frozen tested kernel."""
from pathlib import Path
import shutil,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'phase-audit';assert not dest.exists();(dest/'src').mkdir(parents=True)
old=root.parent/'cache-retention-20261015/analyzer'
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/name,dest/name)
prefix=(root.parent/'toffoli-readiness-20261015/wide-replay/crate/src/main.rs').read_text().split('// Independent reconstruction')[0]
kernel=root/'square-room-b3/src/point_add/tests_positive_phase_polynomial.rs'
(dest/'src/phase_kernel.rs').write_bytes(kernel.read_bytes())
main='''
use quantum_ecc::{circuit,sim};
mod phase_kernel;
struct Outcomes {selected:Vec<usize>,at:usize}
impl XofReader for Outcomes {fn read(&mut self,out:&mut[u8]) {assert_eq!(out.len(),8);let v=if self.selected.contains(&self.at){u64::MAX}else{0u64};self.at+=1;out.copy_from_slice(&v.to_le_bytes());}}
fn main() {
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);
 let ops=load_ops(&args[1]).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());
 let text=std::fs::read_to_string(&args[2]).unwrap();
 let rows:Vec<[U256;6]>=text.lines().enumerate().filter(|(i,_)|i%2==1).take(64).map(|(_,l)|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();assert_eq!(rows.len(),64);
 let mut rng=Outcomes{selected:vec![],at:0};let mut setup=Simulator::new(nq as usize,nb as usize,&mut rng);
 for(lane,v)in rows.iter().enumerate(){assert_eq!(v[1],v[3]);for k in 0..4{setup.set_register(&regs[k],v[k],lane);}}
 let input=setup.qubits.clone();let bits=setup.bits.clone();drop(setup);
 let map:Vec<usize>=ops.iter().enumerate().filter_map(|(i,o)|matches!(o.kind,OperationType::R|OperationType::Hmr).then_some(i)).collect();
 let mut selected=vec![];let mut expected_coefficient=None;
 match phase_kernel::audit(&ops,&input,&bits) {
  Ok(a)=>{println!("FULL_PHASE_PROOF fixed_zero_slope_inputs=64 all_measurements=true max_terms={} measurements={} score=NONE",a.maximum_phase_terms,a.measurements);},
  Err(e)=>{
   println!("FULL_PHASE_DIAG {e} score=NONE");
   if let Some(t)=e.split("first Some(([").nth(1) {
    let (ids,rest)=t.split_once(']').unwrap();selected=ids.split(',').filter(|s|!s.trim().is_empty()).map(|s|s.trim().parse().unwrap()).collect();
    expected_coefficient=rest.trim_start_matches(',').trim().split(')').next().unwrap().parse::<u64>().ok();
    for &mr in &selected {let at=map[mr];println!("PHASE_ORIGIN measurement={mr} op={at}");for i in at.saturating_sub(12)..(at+20).min(ops.len()){println!("PHASE_NEIGHBOR op={i} gate={:?}",ops[i]);}}
   }
  }
 }
 let mut phases=vec![];
 for chosen in [vec![],selected.clone()] {
  let mut rng=Outcomes{selected:chosen.clone(),at:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);s.qubits.clone_from(&input);s.bits.clone_from(&bits);s.apply_iter(ops.iter());
  let wrong=rows.iter().enumerate().filter(|(i,v)|s.get_register(&regs[0],*i)!=v[4]||s.get_register(&regs[1],*i)!=v[5]).count();
  println!("PHASE_WITNESS flipped_measurements={chosen:?} phase={:#x} wrong_values={wrong}",s.phase);phases.push(s.phase);drop(s);assert_eq!(rng.at,map.len());assert_eq!(wrong,0);
 }
 if selected.len()==1 {assert_eq!(phases[0]^phases[1],expected_coefficient.unwrap());assert_ne!(phases[0],phases[1]);println!("SINGLE_MEASUREMENT_FAULT_VERIFIED=true");}
}
'''
(dest/'src/main.rs').write_text(prefix+main)
(root/'phase-manifest.json').write_text(json.dumps({'score':None,'scope':'First64 zero-slope cases in fixed structured packet; unmodified frozen ANF kernel over the complete optimized square-room stream; caps are inconclusive, never a pass.','kernel_sha256':hashlib.sha256(kernel.read_bytes()).hexdigest(),'source_sha256':{str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}},indent=2)+'\n')
