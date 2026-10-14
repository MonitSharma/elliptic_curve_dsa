"""Independent value localization on exact failed points; MR domains unaligned."""
from pathlib import Path
import hashlib, re, subprocess, sys

base, dest, paired = map(Path, sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('create-paired-replay.py')),str(base),str(dest)],check=True)
log = (paired/'run.log').read_text().split('DIAGNOSTIC_ONLY')[-2]
indices = [int(v) for v in re.findall(r'B3_COUNTEREXAMPLE index=(\d+)',log)]
assert len(indices) == len(set(indices)) == 15 and indices[0] == 249
rows = (paired/'candidate.tsv').read_text().splitlines()
selected = [rows[0]]+[rows[i+1] for i in indices]
(dest/'known-official-failures.tsv').write_text('\n'.join(selected)+'\n',newline='\n')
source = (dest/'src/main.rs').read_text().split('fn main() {')[0]
main = r'''
fn main(){
 let a:Vec<String>=std::env::args().collect();assert_eq!(a.len(),4,"stage directory, selected official packet, independent packet");
 let curve=secp256k1();
 for stage in["before-square-guard","after-square-guard","after-linear-restore","final"]{
  let file=std::path::Path::new(&a[1]).join(format!("{stage}.bin"));let ops=load_ops(file.to_str().unwrap()).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());assert_eq!(regs.len(),4);
  let mr=ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count();
  for (packet,mode) in[(&a[2],"official_known_bad"),(&a[3],"independent")]{
   let mut cases=Vec::new();for line in std::fs::read_to_string(packet).unwrap().lines().filter(|l|!l.starts_with('#')&&!l.trim().is_empty()){
    let f:Vec<_>=line.split_whitespace().collect();let values:Vec<_>=f[1..7].iter().map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect();assert!(curve.is_on_curve(values[0],values[1])&&curve.is_on_curve(values[2],values[3]));let expected=curve.add(values[0],values[1],values[2],values[3]);assert_eq!((values[4],values[5]),expected);cases.push((f[0].parse::<usize>().unwrap(),values));
   }
   let(mut bad,mut xb,mut yb,mut phase_shots,mut dirty_batches)=(0,0,0,0,0);
   for(batch,points)in cases.chunks(64).enumerate(){
    let mut h=Shake256::default();h.update(b"product-b3-stage-fixed-mr-v1");h.update(mode.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);
    for(lane,(_,v))in points.iter().enumerate(){for r in 0..4{sim.set_register(&regs[r],v[r],lane);}}
    sim.apply_iter(ops.iter());let live=if points.len()==64{u64::MAX}else{(1u64<<points.len())-1};phase_shots+=(sim.phase&live).count_ones();
    for(lane,(index,v))in points.iter().enumerate(){let x=sim.get_register(&regs[0],lane);let y=sim.get_register(&regs[1],lane);let xbad=x!=v[4];let ybad=y!=v[5];xb+=usize::from(xbad);yb+=usize::from(ybad);bad+=usize::from(xbad||ybad);eprintln!("B3_STAGE_SHOT stage={stage} mode={mode} index={index} x_bad={xbad} y_bad={ybad} phase={} x={x:#x} y={y:#x} expected_x={:#x} expected_y={:#x}",(sim.phase>>lane)&1,v[4],v[5]);}
    for reg in &regs{for q in reg{if let QubitOrBit::Qubit(q)=q{*sim.qubit_mut(*q)=0;}}}dirty_batches+=usize::from(sim.qubits.iter().any(|q|q&live!=0));
   }
   println!("B3_STAGE_DIAGNOSTIC stage={stage} mode={mode} shots={} bad={bad} x_bad={xb} y_bad={yb} phase_shots={phase_shots} dirty_batches={dirty_batches} ops={} nq={nq} nb={nb} measurements={mr} measurement_alignment=NONE score=NONE",cases.len(),ops.len());
  }
 }
}
'''
(dest/'src/main.rs').write_text('const SOURCE_BIND:&str="'+str(base.resolve())+'";\n'+source+main,newline='\n')
print('stage_replay_sha256='+hashlib.sha256((dest/'src/main.rs').read_bytes()).hexdigest())
