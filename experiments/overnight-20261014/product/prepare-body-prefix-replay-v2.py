"""Exact copied Y33 transform, boundary remap and pending logical-wire overlay."""
from pathlib import Path
import subprocess,sys
base,dest,archive=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-body-prefix-replay.py')),str(base),str(dest),str(archive)],check=True)
s=(dest/'src/main.rs').read_text()
copied=(base/'src/point_add/y33_clears.rs').read_text()
copied+='\npub(crate) fn product_sites(ops:&[Op])->Vec<(usize,Vec<usize>,usize)>{find(ops).into_iter().map(|s|(s.q as usize,s.run,s.release)).collect()}\n'
(dest/'src/y33_copy.rs').write_text(copied,newline='\n')
helpers=r'''
mod circuit{pub use quantum_ecc::circuit::*;}
mod y33_copy;
type Event=(usize,Option<usize>);
fn same_op(a:&Op,b:&Op)->bool{a.kind==b.kind&&a.q_control2==b.q_control2&&a.q_control1==b.q_control1&&a.q_target==b.q_target&&a.c_target==b.c_target&&a.c_condition==b.c_condition&&a.r_target==b.r_target}
fn overlay_write(q:&[u64],logical:&mut std::collections::HashMap<usize,u64>,op:&Op){
 let t=op.q_target.0 as usize;
 let v=match op.kind{OperationType::CCX=>{assert!(!logical.contains_key(&(op.q_control1.0 as usize))&&!logical.contains_key(&(op.q_control2.0 as usize)),"source find prohibits pending target reads");q[op.q_control1.0 as usize]&q[op.q_control2.0 as usize]},OperationType::CX=>{assert!(!logical.contains_key(&(op.q_control1.0 as usize)));q[op.q_control1.0 as usize]},OperationType::X=>u64::MAX,_=>panic!("not a Y33 write")};
 *logical.get_mut(&t).expect("logical Y33 target")^=v;
}
#[cfg(test)]mod tests{use super::*;
 #[test]fn exact_y33_overlay_and_mapping(){
  use circuit::{QubitId,NO_BIT};let mut a=Op::empty();a.kind=OperationType::CCX;a.q_control1=QubitId(0);a.q_control2=QubitId(1);a.q_target=QubitId(2);assert_eq!(a.c_condition,NO_BIT);
  let mut x=Op::empty();x.kind=OperationType::X;x.q_target=QubitId(2);let mut r=Op::empty();r.kind=OperationType::R;r.q_target=QubitId(2);
  let old=vec![a.clone(),x.clone(),r];let sites=y33_copy::product_sites(&old);assert_eq!(sites,vec![(2,vec![0,1],2)]);let mut new=old.clone();let mut next=3;y33_copy::sweep(&mut new,&mut next);assert_eq!(next,4);assert_eq!(new.len(),3);assert_eq!(new[0].kind,OperationType::Hmr);assert_eq!(new[1].kind,OperationType::CZ);assert_eq!(new[2].kind,OperationType::Neg);
  for n in 0..8{let q=vec![if n&1!=0{u64::MAX}else{0},if n&2!=0{u64::MAX}else{0},if n&4!=0{u64::MAX}else{0}];let mut overlay=std::collections::HashMap::from([(2,q[2])]);overlay_write(&q,&mut overlay,&a);assert_eq!(overlay[&2],q[2]^(q[0]&q[1]));overlay_write(&q,&mut overlay,&x);assert_eq!(overlay[&2],q[2]^(q[0]&q[1])^u64::MAX);assert_ne!(overlay[&2]^1,overlay[&2],"fault dropped write changes logical value");}
  let mut mutated=old.clone();mutated[1].q_target=QubitId(0);let mut n2=3;y33_copy::sweep(&mut mutated,&mut n2);assert!(!new.iter().zip(&mutated).all(|(a,b)|same_op(a,b)),"fault source mutation detected by exact vector guard");
 }
}
'''
s=s.replace('struct Boundary{','struct Boundary{nb:u32,')
s=s.replace('Boundary{label:', 'Boundary{nb:v[4].parse().unwrap(),label:')
s=s.replace('fn main(){use sha3::Digest;',helpers+'\nfn main(){use sha3::Digest;')
s=s.replace('a.len(),8,"C5raw/C5meta/B3raw/B3meta/knownpoints/independent/archivefinals"','a.len(),10,"C5raw/C5meta/B3raw/B3meta/knownpoints/independent/archivefinals/C5preY33/B3preY33"')
s=s.replace('let ops=load_ops(opfile).unwrap();','let ops=load_ops(opfile).unwrap();let pre=load_ops(if source=="c5_raw"{&a[8]}else{&a[9]}).unwrap();')
start=s.index('  assert_eq!(boundaries.len(),7);')
end=s.index('  for(packet,mode)',start)
s=s[:start]+r'''
  assert_eq!(boundaries.len(),9);assert_eq!(pre.len(),ops.len());assert_eq!(boundaries.last().unwrap().end,ops.len());
  let by33=boundaries.iter().find(|b|b.label=="before-y33").unwrap();let ay33=boundaries.iter().find(|b|b.label=="after-y33").unwrap();assert_eq!(by33.end,pre.len());
  let mut exact=pre.clone();let mut next=by33.nb;y33_copy::sweep(&mut exact,&mut next);assert_eq!(next,ay33.nb);assert_eq!(exact.len(),ops.len());assert!(exact.iter().zip(&ops).all(|(a,b)|same_op(a,b)),"copied source Y33 sweep exact entire final raw OpVec equality");drop(exact);
  let sites=y33_copy::product_sites(&pre);let mut events=std::collections::BTreeMap::<usize,Event>::new();for(k,(_,run,release))in sites.iter().enumerate(){for(g,&i)in run.iter().enumerate(){assert!(events.insert(i,(k,Some(g))).is_none());}assert!(events.insert(*release,(k,None)).is_none());}
  let mut ph=sha3::Sha3_256::new();let mut fh=sha3::Sha3_256::new();let(mut pa,mut fa)=(0,0);for b in &boundaries{let final_domain=matches!(b.label.as_str(),"after-y33"|"before-finalize-records"|"after-finalize-records");if final_domain{for o in &ops[fa..b.end]{canonical_update(&mut fh,o);}fa=b.end;assert_eq!(format!("{:x}",fh.clone().finalize()),b.hash,"final-domain metadata hash {}",b.label);}else{for o in &pre[pa..b.end]{canonical_update(&mut ph,o);}pa=b.end;assert_eq!(format!("{:x}",ph.clone().finalize()),b.hash,"original emission-domain metadata hash {}",b.label);}}
  assert_eq!(boundaries[7].hash,boundaries[8].hash);eprintln!("PRODUCT_BODY_MAPPING source={source} all9domainhashes=true exact_copied_y33_vector=true sites={} finalize_records_changed_ops=false phase_alignment=WITHIN_SOURCE_ONLY runtime_library={} score=NONE",sites.len(),SOURCE_BIND);
''' +s[end:]
start=s.index('    for b in &boundaries{for op in &ops[start..b.end]')
end=s.index('let(mut xb,mut yb)=(0,0);',start)+len('let(mut xb,mut yb)=(0,0);')
s=s[:start]+r'''
    let mut final_at=0usize;let mut logical=std::collections::HashMap::<usize,u64>::new();
    for b in &boundaries{let old_end=b.end;while start<old_end{
      let ev=events.range(start..old_end).next().map(|(&i,&e)|(i,e));let stop=ev.map(|e|e.0).unwrap_or(old_end);let n=stop-start;
      for op in &pre[start..stop]{match op.kind{OperationType::PushCondition=>depth+=1,OperationType::PopCondition=>depth-=1,_=>{}}}
      sim.apply_iter(ops[final_at..final_at+n].iter());start=stop;final_at+=n;
      if let Some((i,(k,g)))=ev{assert_eq!(start,i);let q=sites[k].0;match g{None=>{assert!(logical.remove(&q).is_some());},Some(g)=>{if g==0{assert!(logical.insert(q,sim.qubits[q]).is_none());assert_eq!(ops[final_at].kind,OperationType::Hmr);sim.apply_iter(ops[final_at..final_at+1].iter());final_at+=1;}overlay_write(&sim.qubits,&mut logical,&pre[i]);sim.apply_iter(ops[final_at..final_at+1].iter());final_at+=1;}}start+=1;}
    }
    assert_eq!(depth,0,"body boundary outside classical scope");let starts=sites.iter().filter(|s|s.1[0]<old_end).count();let releases=sites.iter().filter(|s|s.2<old_end).count();assert_eq!(final_at,old_end+starts-releases);assert_eq!(logical.len(),starts-releases);
    let mut logical_q=sim.qubits.clone();for(&q,&v)in &logical{logical_q[q]=v;}let(mut xb,mut yb)=(0,0);
''' +s[end:]
s=s.replace('readq(&sim.qubits,&b.x,lane)','readq(&logical_q,&b.x,lane)').replace('readq(&sim.qubits,&b.y,lane)','readq(&logical_q,&b.y,lane)').replace('sim.qubits[*b.r0.last().unwrap()]','logical_q[*b.r0.last().unwrap()]').replace('(sim.qubits[q]>>lane)','(logical_q[q]>>lane)')
s=s.replace('"final-coordinates"|"before-finalize-records"','"final-coordinates"|"before-y33"|"after-y33"|"before-finalize-records"')
s=s.replace('end={} x_low=', 'end={} final_end={final_at} pending_y33={} physical_x={:#x} physical_y={:#x} value_frame=LOGICAL_PRE_Y33 x_low=')
s=s.replace('b.label,b.end);','b.label,b.end,logical.len(),readq(&sim.qubits,&b.x,lane),readq(&sim.qubits,&b.y,lane));')
s=s.replace('if b.label=="after-finalize-records"{assert_eq!', 'if b.label=="after-finalize-records"{assert!(logical.is_empty());assert_eq!(final_at,ops.len());assert_eq!')
s=s.replace('finalizedprefixhashes_verified=true','exact_y33_transform_and_both_hashdomains_verified=true logical_boundary_overlay=true')
(dest/'src/main.rs').write_text(s,newline='\n')
