"""Actual-source prefix replay plus independent all-MR component checks."""
from pathlib import Path
import json, subprocess, sys
base, dest, manifest, kernel = map(Path, sys.argv[1:5])
subprocess.run([sys.executable,str(Path(__file__).with_name('create-paired-replay.py')),str(base),str(dest)],check=True)
rows=json.loads(manifest.read_text())['rows']
rows=[r for r in rows if r['payload'] is not None and not r['payload'][0] and r['fin']==0 and not r['ttm'] and r['drop']==0]
assert len(rows)==105
lines=[]
for r in rows:
 q,b,nb=r['entry_state'];nq,dnb=r['entry_dims'];assert nb==dnb
 fields=[r['payload'][1],r['entry_op'],r['exit_op'],nq,nb]
 lines.append('\t'.join(map(str,fields))+ '\t'+'\t'.join(','.join(map(str,ids))for ids in[r['acc'],r['e'],r['nm'],r['k'],q,b]))
(dest/'contexts.tsv').write_text('\n'.join(lines)+'\n',newline='\n')
(dest/'src/product_phase_kernel.rs').write_bytes(kernel.read_bytes())
source=(dest/'src/main.rs').read_text().split('fn main() {')[0]
source='use quantum_ecc::circuit;\n#[path="product_phase_kernel.rs"]mod kernel;\n'+source
main=r'''
struct Context{tick:usize,start:usize,end:usize,nq:usize,nb:usize,acc:Vec<usize>,e:Vec<usize>,nm:Vec<usize>,k:Vec<usize>,freeq:Vec<usize>,freeb:Vec<usize>,old:Vec<Op>,new:Vec<Op>}
fn reference(x:u64,e:u64,n:u64,s:u64,mw:usize)->u64{let r=n+(x&7);let low=(x&63)+e+((r&1)<<4)+(((r^(r>>1))&1)<<5);let y=((s!=0)as u64)*(low>>3&1)+2*(s>>1&1)*(low>>4&1)+4*((s&1)&(s>>1&1))*(low>>5&1);let borrow=((x&7)+e>=8)as i128;let k=r as i128+8*(y as i128-borrow);((x as i128+e as i128-((1i128<<32)+976)*k)&((1i128<<mw)-1))as u64}
fn read(q:&[u64],ids:&[usize],lane:usize)->u64{ids.iter().enumerate().map(|(i,&id)|((q[id]>>lane)&1)<<i).sum()}
fn main(){
 let a:Vec<String>=std::env::args().collect();assert_eq!(a.len(),7,"rawbody, contexts, components, independent.tsv, structured.tsv, output.tsv");
 let raw=load_ops(&a[1]).unwrap();assert_eq!(raw.len(),11269441);let(nq,nb,_,regs)=analyze_ops(raw.iter());assert_eq!(regs.len(),4);
 let mut contexts=Vec::new();for line in std::fs::read_to_string(&a[2]).unwrap().lines(){let f:Vec<_>=line.split('\t').collect();let number=|i:usize|f[i].parse::<usize>().unwrap();let ids=|i:usize|if f[i].is_empty(){Vec::new()}else{f[i].split(',').map(|n|n.parse::<usize>().unwrap()).collect()};let tick=number(0);let path=|kind:&str|std::path::Path::new(&a[3]).join(format!("tick{tick}-{kind}.bin"));let old=load_ops(path("old").to_str().unwrap()).unwrap();let new=load_ops(path("new").to_str().unwrap()).unwrap();assert_eq!(old,raw[number(1)..number(2)],"EXACT original raw slice tick{tick}");contexts.push(Context{tick,start:number(1),end:number(2),nq:number(3),nb:number(4),acc:ids(5),e:ids(6),nm:ids(7),k:ids(8),freeq:ids(9),freeb:ids(10),old,new});}
 assert_eq!(contexts.len(),105);eprintln!("PRODUCT_H45_ORIGINAL_SLICES all105_byte_equal=true raw_ops={} runtime_library={} score=NONE",raw.len(),SOURCE_BIND);
 let mut output=File::create(&a[6]).unwrap();writeln!(output,"# family batch tick old_sample_T new_sample_T allMR true freebit_stale_patterns actual,ones,a5").unwrap();
 let(mut proofs,mut native_cases,mut component_slots)=(0usize,0usize,0usize);
 for(packet,family)in[(&a[4],"independent"),(&a[5],"structured")]{
  let mut points=Vec::new();for line in std::fs::read_to_string(packet).unwrap().lines().filter(|l|!l.starts_with('#')&&!l.trim().is_empty()){let f:Vec<_>=line.split_whitespace().collect();points.push(f[1..5].iter().map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>());}assert_eq!(points.len(),256);
  for(batch,points)in points.chunks(64).enumerate(){let mut h=Shake256::default();h.update(b"product-h45-actual-prefix-native-v1");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);for(lane,p)in points.iter().enumerate(){for r in 0..4{sim.set_register(&regs[r],p[r],lane);}}
   let(mut cursor,mut depth)=(0usize,0isize);
   for ctx in &contexts{
    for op in &raw[cursor..ctx.start]{match op.kind{OperationType::PushCondition=>depth+=1,OperationType::PopCondition=>depth-=1,_=>{}}}assert_eq!(depth,0,"actual fold external condition stack");sim.apply_iter(raw[cursor..ctx.start].iter());let initial_q=sim.qubits[..ctx.nq].to_vec();let initial_b=sim.bits[..ctx.nb].to_vec();assert!(ctx.freeq.iter().all(|&q|initial_q[q]==0),"actual freeq nonzero tick{}",ctx.tick);
    let mut expected=initial_q.clone();for lane in 0..64{let x=read(&initial_q,&ctx.acc,lane);let e=read(&initial_q,&ctx.e,lane);let n=read(&initial_q,&ctx.nm,lane);let s=read(&initial_q,&ctx.k,lane);let want=reference(x,e,n,s,ctx.acc.len());for(i,&id)in ctx.acc.iter().enumerate(){expected[id]&=!(1u64<<lane);expected[id]|=((want>>i)&1)<<lane;}}
    let mut actual_cost=[0u64;2];
    for stale in 0..3{let mut b=initial_b.clone();if stale!=0{let word=if stale==1{u64::MAX}else{0xa5a5a5a5a5a5a5a5};for i in 512..b.len(){b[i]=word;}for &i in &ctx.freeb{b[i]=word;}}
     for(which,ops)in[&ctx.old,&ctx.new].iter().enumerate(){let audit=kernel::audit(ops,&initial_q,&b).unwrap_or_else(|e|panic!("actual prefix family={family} batch={batch} tick={} stale={stale}: {e}",ctx.tick));assert_eq!(audit.qubits,expected,"actual point arithmetic/allq");proofs+=64;
      let mut h=Shake256::default();h.update(b"product-h45-component-native-v1");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());h.update(&(ctx.tick as u64).to_le_bytes());h.update(&(stale as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut component=Simulator::new(ctx.nq,ctx.nb,&mut rng);component.qubits.clone_from(&initial_q);component.bits.clone_from(&b);component.phase=sim.phase;component.apply_iter(ops.iter());assert_eq!(component.qubits,expected);assert_eq!(component.phase,sim.phase);for i in 0..ctx.nb{if !ctx.freeb.contains(&i){assert_eq!(component.bits[i],b[i],"all live classic preserved");}}native_cases+=64;if stale==0{actual_cost[which]=component.stats.toffoli_gates;}
     }
    }
    writeln!(output,"{family}\t{batch}\t{}\t{}\t{}\ttrue",ctx.tick,actual_cost[0]as f64/64.,actual_cost[1]as f64/64.).unwrap();component_slots+=1;
    sim.apply_iter(raw[ctx.start..ctx.end].iter());cursor=ctx.end;
    eprintln!("PRODUCT_H45_ACTUAL_PREFIX family={family} batch={batch} tick={} allMR_allq_liveclass_phase_PASS=true initial_freeq_zero=true scratch_patterns=actual,ones,a5 source_original_slice_equal=true score=NONE",ctx.tick);
   }
  }
 }
 println!("PRODUCT_H45_ACTUAL_PREFIX_TOTAL source_contexts=105 admitted104 actual_point_cases=512 component_slots={component_slots} fixedpoint_allMR_proofs={proofs} native_cases={native_cases} score=NONE");
}
'''
(dest/'src/main.rs').write_text('const SOURCE_BIND:&str="'+str(base.resolve())+'";\n'+source+main,newline='\n')
