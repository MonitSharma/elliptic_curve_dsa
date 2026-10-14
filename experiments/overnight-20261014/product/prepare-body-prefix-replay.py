"""Aligned-within-source native boundary replay, attested against archived finals."""
from pathlib import Path
import re, subprocess, sys
base,dest,archive=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('create-paired-replay.py')),str(base),str(dest)],check=True)
source=(dest/'src/main.rs').read_text().split('fn main() {')[0]
lines=[]
for line in (archive/'run.log').read_text().splitlines():
 if not line.startswith('B3_STAGE_SHOT '):continue
 f=dict(re.findall(r'(\w+)=(\S+)',line))
 if f['stage'] not in['c5_raw','b3_raw']:continue
 lines.append('\t'.join(f[k]for k in['stage','mode','index','x','y','phase']))
(dest/'expected-finals.tsv').write_text('\n'.join(lines)+'\n',newline='\n')
assert len(lines)==542
main=r'''
struct Boundary{label:String,end:usize,hash:String,seams:bool,offset:U256,x:Vec<usize>,y:Vec<usize>,ox:Vec<usize>,oy:Vec<usize>,r0:Vec<usize>}
fn readq(q:&[u64],ids:&[usize],lane:usize)->U256{assert!(ids.len()<=256);let mut v=U256::ZERO;for(i,&id)in ids.iter().enumerate(){if(q[id]>>lane)&1!=0{v|=U256::from(1)<<i;}}v}
fn canonical_update(h:&mut sha3::Sha3_256,o:&Op){use sha3::Digest;Digest::update(h,(o.kind as u32).to_le_bytes());Digest::update(h,[0u8;4]);for id in[o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{Digest::update(h,id.to_le_bytes());}}
fn main(){use sha3::Digest;let a:Vec<String>=std::env::args().collect();assert_eq!(a.len(),8,"C5raw/C5meta/B3raw/B3meta/knownpoints/independent/archivefinals");let curve=secp256k1();let p=curve.modulus;let sub=quantum_ecc::weierstrass_elliptic_curve::sub_mod;let f=U256::from(2).pow(U256::from(32))+U256::from(977);
 let mut archived=std::collections::HashMap::new();for line in std::fs::read_to_string(&a[7]).unwrap().lines(){let v:Vec<_>=line.split_whitespace().collect();archived.insert((v[0].to_string(),v[1].to_string(),v[2].parse::<usize>().unwrap()),(U256::from_str_radix(v[3].trim_start_matches("0x"),16).unwrap(),U256::from_str_radix(v[4].trim_start_matches("0x"),16).unwrap(),v[5].parse::<u64>().unwrap()));}
 for(source,opfile,metafile)in[("c5_raw",&a[1],&a[2]),("b3_raw",&a[3],&a[4])]{let ops=load_ops(opfile).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());let mut boundaries=Vec::new();for line in std::fs::read_to_string(metafile).unwrap().lines(){let v:Vec<_>=line.split('\t').collect();assert_eq!(v.len(),12);let ids=|i:usize|if v[i]=="-"{Vec::new()}else{v[i].split(',').map(|x|x.parse::<usize>().unwrap()).collect()};boundaries.push(Boundary{label:v[0].into(),end:v[1].parse().unwrap(),hash:v[2].into(),seams:v[5]=="true",offset:U256::from_str_radix(v[6].trim_start_matches("0x"),16).unwrap(),x:ids(7),y:ids(8),ox:ids(9),oy:ids(10),r0:ids(11)});}
  assert_eq!(boundaries.len(),7);assert_eq!(boundaries.last().unwrap().end,ops.len());let mut hash=sha3::Sha3_256::new();let mut at=0;for b in &boundaries{for o in &ops[at..b.end]{canonical_update(&mut hash,o);}assert_eq!(format!("{:x}",hash.clone().finalize()),b.hash,"actual finalized rawprefix hash {}",b.label);at=b.end;}
  assert_eq!(boundaries[5].end,boundaries[6].end);assert_eq!(boundaries[5].hash,boundaries[6].hash);eprintln!("PRODUCT_BODY_MAPPING source={source} all7prefixhashes=true finalize_records_changed_ops=false phase_alignment=WITHIN_SOURCE_ONLY runtime_library={} score=NONE",SOURCE_BIND);
  for(packet,mode)in[(&a[5],"official_known_bad"),(&a[6],"independent")]{let mut cases=Vec::new();for line in std::fs::read_to_string(packet).unwrap().lines().filter(|l|!l.starts_with('#')&&!l.trim().is_empty()){let v:Vec<_>=line.split_whitespace().collect();let point=v[1..7].iter().map(|s|U256::from_str_radix(s.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>();assert_eq!(curve.add(point[0],point[1],point[2],point[3]),(point[4],point[5]));cases.push((v[0].parse::<usize>().unwrap(),point));}
   for(batch,cases)in cases.chunks(64).enumerate(){let mut h=Shake256::default();h.update(b"product-b3-stage-fixed-mr-v1");h.update(mode.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);for(lane,(_,v))in cases.iter().enumerate(){for r in 0..4{sim.set_register(&regs[r],v[r],lane);}}let(mut start,mut depth)=(0usize,0isize);
    for b in &boundaries{for op in &ops[start..b.end]{match op.kind{OperationType::PushCondition=>depth+=1,OperationType::PopCondition=>depth-=1,_=>{}}}assert_eq!(depth,0,"body boundary outsideclassicalscope");sim.apply_iter(ops[start..b.end].iter());start=b.end;let(mut xb,mut yb)=(0,0);
     for(lane,(index,v))in cases.iter().enumerate(){let lambda=sub(v[1],v[3],p).mul_mod(sub(v[0],v[2],p).inv_mod(p).unwrap(),p);let low=readq(&sim.qubits,&b.x,lane);let y_low=readq(&sim.qubits,&b.y,lane);let y=y_low.reduce_mod(p);let mut x=low.reduce_mod(p);let mut uniform=true;if !b.r0.is_empty(){assert_eq!(&b.r0[..256],&b.x);let sg=(sim.qubits[*b.r0.last().unwrap()]>>lane)&1;uniform=b.r0[256..].iter().all(|&q|(sim.qubits[q]>>lane)&1==sg);if sg!=0{x=sub(x,f,p);}}
      let (ex,ey)=match b.label.as_str(){"coord-y-sub"=>(if b.seams{v[0]}else{sub(v[0],v[2],p)},sub(v[1],v[3],p)),"divide-seamed"=>(v[0].add_mod(v[2].add_mod(v[2],p),p).add_mod(b.offset,p),lambda),"sub-square"=>(sub(v[0].add_mod(v[2].add_mod(v[2],p),p),lambda.mul_mod(lambda,p),p),lambda),"multiply-seamed"=>(v[4],v[5].add_mod(v[3],p)),"final-coordinates"|"before-finalize-records"|"after-finalize-records"=>(v[4],v[5]),_=>panic!("unknownboundary")};
      let xok=x==ex;let yok=y==ey;xb+=usize::from(!xok);yb+=usize::from(!yok);let classic=readq(&sim.bits,&b.ox,lane)==v[2]&&readq(&sim.bits,&b.oy,lane)==v[3];let phase=(sim.phase>>lane)&1;
      println!("PRODUCT_BODY_POINT source={source} mode={mode} batch={batch} index={index} boundary={} end={} x_low={low:#x} x_residue={x:#x} y={y:#x} expected_x={ex:#x} expected_y={ey:#x} x_correct={xok} y_correct={yok} extension_uniform={uniform} classic_inputs_retained={classic} phase={phase} aligned_within_source=true cross_source_phase_alignment=NONE score=NONE",b.label,b.end);
      if b.label=="after-finalize-records"{assert_eq!((low,y_low,phase),archived[&(source.to_string(),mode.to_string(),*index)],"fullraw archivepoint identity");}
     }
     eprintln!("PRODUCT_BODY_BOUNDARY_CHECK source={source} mode={mode} batch={batch} boundary={} shots={} x_bad={xb} y_bad={yb} score=NONE",b.label,cases.len());
    }
   }
  }
 }
 println!("PRODUCT_BODY_TOTAL sources=2 points_per_source=271 finalizedprefixhashes_verified=true archived_final_values_and_phase_verified=true continuous_raw_rng=true score=NONE");
}
'''
(dest/'src/main.rs').write_text('const SOURCE_BIND:&str="'+str(base.resolve())+'";\n'+source+main,newline='\n')
