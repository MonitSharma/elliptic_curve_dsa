from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
old = root.parent / 'zero-mr-20261016'
tool = root / 'tool'
(tool / 'src').mkdir(parents=True, exist_ok=True)
for name in ['Cargo.toml', 'Cargo.lock', 'simd8wide.h']:
    shutil.copyfile(old / 'tool' / name, tool / name)
for name in ['prefix.rs', 'fast_sim_wide.rs']:
    shutil.copyfile(old / 'tool/src' / name, tool / 'src' / name)
for name in ['zero8.c', 'build.rs']:
    shutil.copyfile(old / name, tool / name)
source = (old / 'main.rs').read_text()
slice_source = r'''
// Conservative reverse liveness at fixed MR=0. Live scopes retain their
// entry-time classical snapshot. Only final coordinate values are queried.
fn slice(p:&Compact, regs:&[Vec<QubitOrBit>], nq:usize, nb:usize, prune_scopes:bool)->Compact {
 let mut qlive=vec![false;nq]; let mut blive=vec![false;nb];
 for reg in &regs[..2] { for w in reg { match w {
  QubitOrBit::Qubit(id)=>qlive[id.0 as usize]=true,
  QubitOrBit::Bit(id)=>blive[id.0 as usize]=true,
 } } }
 let mut keep=vec![false;p.ops.len()];
 let mut rng_obligations=Vec::new();
 let mut scopes:Vec<(usize,bool)>=Vec::new();
 let mut depth=0usize;
 let unconditional=p.ops.iter().map(|o| {
  let yes=depth==0&&o.c==u32::MAX;
  if o.k==15 {depth+=1;} else if o.k==16 {depth-=1;}
  yes
 }).collect::<Vec<_>>();assert_eq!(depth,0);
 for (i,o) in p.ops.iter().enumerate().rev() {
  if prune_scopes&&o.k==16 {scopes.push((i,false));continue;}
  if prune_scopes&&o.k==15 {
   let (end,active)=scopes.pop().unwrap();
   if active {
    keep[i]=true;keep[end]=true;blive[o.c as usize]=true;
    if let Some(scope)=scopes.last_mut(){scope.1=true;}
   }
   continue;
  }
  let needed=match o.k {
   15|16=>true,
   3|4|5=>blive[o.bt as usize],
   6|8|11|13=>qlive[o.t as usize],
   10=>qlive[o.t as usize]||qlive[o.a as usize],
   12=>qlive[o.t as usize]||blive[o.bt as usize],
   0|7|9|14=>false,
   _=>panic!("unknown opcode {}",o.k),
  };
  if !needed {continue;} keep[i]=true;
  if o.k==12&&blive[o.bt as usize]{rng_obligations.push((i,o.bt));}
  if let Some(scope)=scopes.last_mut(){scope.1=true;}
  if unconditional[i] {
   match o.k {
    4|5=>blive[o.bt as usize]=false,
    11=>qlive[o.t as usize]=false,
    12=>{qlive[o.t as usize]=false;blive[o.bt as usize]=false;},
    10=>{let a=qlive[o.a as usize];qlive[o.a as usize]=qlive[o.t as usize];qlive[o.t as usize]=a;},
    _=>{},
   }
  }
  if o.c!=u32::MAX {blive[o.c as usize]=true;}
  match o.k {
   8=>qlive[o.a as usize]=true,
   10 if !unconditional[i]=>{qlive[o.a as usize]=true;qlive[o.t as usize]=true;},
   13=>{qlive[o.a as usize]=true;qlive[o.b as usize]=true;},
   _=>{},
  }
 }
 assert!(scopes.is_empty());
 println!("SLICE_RNG_OBLIGATIONS input_ops={} live_HMR_definitions={} sample={:?}",p.ops.len(),rng_obligations.len(),&rng_obligations[..rng_obligations.len().min(24)]);
 if p.ops.len()>10_000_000 {let text=rng_obligations.iter().map(|(i,b)|format!("{i},{b}\\n")).collect::<String>();fs::write(format!("rng-obligations-{}.csv",p.ops.len()),format!("compact_op,classical_target\\n{text}")).unwrap();}
 let ops=p.ops.iter().zip(keep).filter_map(|(o,k)|k.then_some(*o)).collect::<Vec<_>>();
 println!("SLICE before={} after={} outputs=registers0and1 prune_scopes={prune_scopes}",p.ops.len(),ops.len());
 Compact{ops,rng_count:0}
}
fn same_outputs(aq:&[u64],ab:&[u64],bq:&[u64],bb:&[u64],regs:&[Vec<QubitOrBit>]) {
 for reg in &regs[..2] {for w in reg {for j in 0..8 {match w {
  QubitOrBit::Qubit(id)=>assert_eq!(aq[id.0 as usize*8+j],bq[id.0 as usize*8+j]),
  QubitOrBit::Bit(id)=>assert_eq!(ab[id.0 as usize*8+j],bb[id.0 as usize*8+j]),
 }}}}
}
// A separate research-only opcode range specializes depth-zero unconditional
// gates. Pushed guards and conditional gates retain the original interpreter.
fn specialize(p:&Compact)->Compact {
 let mut ops=p.ops.clone();let mut depth=0usize;let mut count=0usize;
 for o in &mut ops {
  if depth==0&&o.c==u32::MAX&&matches!(o.k,3|4|5|6|8|10|11|12|13){o.k+=32;count+=1;}
  if o.k==15{depth+=1;}else if o.k==16{depth-=1;}
 }
 assert_eq!(depth,0);println!("SPECIALIZED unconditional_ops={count}");Compact{ops,rng_count:0}
}
fn slice_fixtures(){
 let nil=u32::MAX;
 let op=|k,a,b,t,bt,c|CompactOp{a,b,t,k,pad:0,bt,c};
 let fixture=Compact{rng_count:0,ops:vec![
  op(15,0,0,0,0,0),op(3,0,0,0,0,nil),
  op(6,0,0,0,0,nil),op(15,0,0,0,0,1),
  op(8,0,0,1,0,nil),op(13,0,1,2,0,nil),
  op(12,0,0,3,2,1),op(16,0,0,0,0,nil),
  op(10,1,0,2,0,2),op(16,0,0,0,0,nil),
  op(11,0,0,3,0,nil),op(4,0,0,0,3,nil),
  op(6,0,0,3,0,nil),op(5,0,0,0,3,nil),
  op(15,0,0,0,0,3),op(6,0,0,3,0,nil),op(16,0,0,0,0,nil),
  op(10,2,0,0,0,nil),op(12,0,0,3,2,nil),
 ]};
 let regs=vec![vec![QubitOrBit::Qubit(QubitId(0)),QubitOrBit::Qubit(QubitId(1))],vec![QubitOrBit::Qubit(QubitId(2))]];
 let sliced=slice(&fixture,&regs,4,4,true);let allscopes=slice(&fixture,&regs,4,4,false);let specialized=specialize(&sliced);
 let mut q=vec![0u64;32];let mut b=vec![0u64;32];for j in 0..8{for lane in 0..64{let value=j*64+lane;for i in 0..4{q[i*8+j]|=(((value>>i)&1)as u64)<<lane;b[i*8+j]|=(((value>>(i+4))&1)as u64)<<lane;}}}
 let mut stack=vec![0;4096*8];let(mut expectedq,mut expectedb)=(q.clone(),b.clone());run(&fixture,&mut expectedq,&mut expectedb,&mut stack);
 for code in [&sliced,&allscopes,&specialized]{let(mut actualq,mut actualb)=(q.clone(),b.clone());run(code,&mut actualq,&mut actualb,&mut stack);same_outputs(&expectedq,&expectedb,&actualq,&actualb,&regs);}
 // Removing the first live X must change a queried output on some assignment.
 let mut mutant=Compact{ops:sliced.ops.clone(),rng_count:0};let at=mutant.ops.iter().position(|o|o.k==6&&o.t==0).unwrap();mutant.ops.remove(at);let(mut mq,mut mb)=(q,b);run(&mutant,&mut mq,&mut mb,&mut stack);assert!((0..3).any(|i|(0..8).any(|j|mq[i*8+j]!=expectedq[i*8+j])));
 println!("SLICE_FIXTURES assignments=512 quantum_and_classical_inputs=8 nested_guard_snapshot=true overwrite_kills=true dead_scope=true negative_live_gate_removal=true");
}
'''
source = source.replace('fn main(){', slice_source + '\nfn main(){', 1)
source = source.replace('let a:Vec<_>=std::env::args().collect();', 'slice_fixtures();let a:Vec<_>=std::env::args().collect();',1)
source = source.replace('let rows=fs::read_to_string', '''let full_liveness=slice(&p,&regs,nq as usize,nb as usize,true);println!("FULL_UNSIMPLIFIED_LIVENESS coordinate_cone_ops={}",full_liveness.ops.len());drop(full_liveness);
 let sliced=slice(&simplified,&regs,nq as usize,nb as usize,true);let allscopes=slice(&simplified,&regs,nq as usize,nb as usize,false);let specialized=specialize(&sliced);
 if a.len()>3 {
  let mut data=Vec::with_capacity(specialized.ops.len()*16);
  for o in &specialized.ops {data.extend_from_slice(&o.a.to_le_bytes());data.extend_from_slice(&o.b.to_le_bytes());data.extend_from_slice(&o.t.to_le_bytes());data.push(o.k);data.push(o.pad);data.extend_from_slice(&o.c.to_le_bytes());data.extend_from_slice(&o.bt.to_le_bytes());}
  fs::write(&a[3],data).unwrap();
  let mut meta=format!("ops\\t{}\\nqubits\\t{nq}\\nclassical_bits\\t{nb}\\nrejection_enabled\\tfalse\\nrng\\tfixed all-zero\\nphase\\tnot queried\\n",specialized.ops.len());
  for (r,reg) in regs[..2].iter().enumerate(){for (bit,w) in reg.iter().enumerate(){let (kind,id)=match w{QubitOrBit::Qubit(id)=>("q",id.0),QubitOrBit::Bit(id)=>("b",id.0)};meta.push_str(&format!("output\\t{r}\\t{bit}\\t{kind}\\t{id}\\n"));}}
  fs::write(format!("{}.tsv",a[3]),meta).unwrap();
 }
 let rows=fs::read_to_string''', 1)
source = source.replace('println!("ZERO_VALUE_VERIFIED', 'for code in [&sliced,&allscopes,&specialized]{let(mut sliceq,mut sliceb)=(q.clone(),b.clone());run(code,&mut sliceq,&mut sliceb,&mut stack);same_outputs(&sq,&sb,&sliceq,&sliceb,&regs);}\n println!("SLICE_VERIFIED shots=512 output_registers0and1=true phase_not_queried=true rejection_disabled=true");\n println!("ZERO_VALUE_VERIFIED', 1)
source = source.replace('[("full",&p),("static_simplified",&simplified)]', '[("full",&p),("static_simplified",&simplified),("all_scopes_slice",&allscopes),("output_slice",&sliced),("specialized_slice",&specialized)]')
source = source.replace('assert_eq!(qq,sq);assert_eq!(bb,sb);', 'same_outputs(&qq,&bb,&sq,&sb,&regs);')
(tool / 'src/main.rs').write_text(source)
kernel=(old/'zero8.c').read_text()
kernel=kernel.replace('switch(o.k){','''switch(o.k){
   case 35:st(bits,o.bt,X(ld(bits,o.bt),_mm512_set1_epi64(-1)));break;
   case 36:st(bits,o.bt,_mm512_setzero_si512());break;
   case 37:st(bits,o.bt,_mm512_set1_epi64(-1));break;
   case 38:st(q,o.t,X(ld(q,o.t),_mm512_set1_epi64(-1)));break;
   case 40:st(q,o.t,X(ld(q,o.t),ld(q,o.a)));break;
   case 42:x=ld(q,o.t);y=ld(q,o.a);st(q,o.t,y);st(q,o.a,x);break;
   case 43:st(q,o.t,_mm512_setzero_si512());break;
   case 44:st(q,o.t,_mm512_setzero_si512());st(bits,o.bt,_mm512_setzero_si512());break;
   case 45:st(q,o.t,X(ld(q,o.t),A(ld(q,o.a),ld(q,o.b))));break;
''',1)
(tool/'zero8.c').write_text(kernel)
