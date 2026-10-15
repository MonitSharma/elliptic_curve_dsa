fn load_mask_program(path:&str)->MaskProgram{let data=std::fs::read(path).unwrap();assert_eq!(&data[..8],b"MRMASK01");let read64=|off|u64::from_le_bytes(data[off..off+8].try_into().unwrap())as usize;let n=read64(8);let inputs=read64(16);let outputs=read64(24);assert!(n>=2&&n<100000000);assert_eq!(inputs,1024);assert_eq!(outputs,512);assert_eq!(data.len(),32+n*16+outputs*4);let read32=|off|u32::from_le_bytes(data[off..off+4].try_into().unwrap());let mut nodes=Vec::with_capacity(n);for i in 0..n{let off=32+i*16;let node=MaskNode{kind:read32(off),a:read32(off+4),b:read32(off+8),aux:read32(off+12)};assert_eq!(node.aux,0);match node.kind{0|1=>{},2=>assert!((node.a as usize)<inputs),3|4|5=>assert!((node.a as usize)<i&&(node.b as usize)<i),_=>panic!("unknown mask terminal")};nodes.push(node);}let roots=(0..outputs).map(|i|{let r=read32(32+n*16+i*4);assert!((r as usize)<n);r}).collect();MaskProgram{nodes,roots,inputs,old_live:0}}
struct ZeroReader;impl XofReader for ZeroReader{fn read(&mut self,out:&mut[u8]){out.fill(0);}}
fn validation_random(seed:u64)->sha3::Shake256Reader{let mut h=Shake256::default();h.update(b"mr-mask-independent-protected-v1");h.update(&seed.to_le_bytes());h.finalize_xof()}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),5,"candidate mask fixture original");
 let ops=load_ops(&args[1]).unwrap();let original=load_ops(&args[4]).unwrap();let program=load_mask_program(&args[2]);
 let(nq,nb,_,regs)=analyze_ops(ops.iter());let(onq,onb,_,oregs)=analyze_ops(original.iter());
 assert_eq!(regs.len(),4);assert_eq!(oregs.len(),4);assert!(regs.iter().chain(&oregs).all(|r|r.len()==256));
 let rows:Vec<Vec<U256>>=std::fs::read_to_string(&args[3]).unwrap().lines().filter(|l|!l.trim().is_empty()).map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect()).collect();assert!(rows.iter().all(|r|r.len()==6));
 let placeholder=args[3].contains("sensitivity-arbitrary");let timer=std::time::Instant::now();let(mut batches,mut knownbits,mut wrong_count)=(0,0usize,0usize);
 for data in rows.chunks(64){
  let mut zr=ZeroReader;let mut zero=Simulator::new(onq as usize,onb as usize,&mut zr);let mut expected=vec![0u64;512];
  for(lane,row)in data.iter().enumerate(){for(reg,value)in oregs[..4].iter().zip(&row[..4]){zero.set_register(reg,*value,lane);}for reg in 0..2{for bit in 0..256{expected[reg*256+bit]|=(row[4+reg].bit(bit)as u64)<<lane;}}}
  let input:Vec<u64>=oregs.iter().flatten().map(|w|match w{QubitOrBit::Qubit(id)=>zero.qubits[id.0 as usize],QubitOrBit::Bit(id)=>zero.bits[id.0 as usize]}).collect();
  let known=program.eval(&input);let active=if data.len()==64{u64::MAX}else{(1u64<<data.len())-1};knownbits+=known.iter().map(|m|(m&active).count_ones()as usize).sum::<usize>();zero.apply_iter(original.iter());
  let output:Vec<_>=oregs[..2].iter().flatten().map(|w|match w{QubitOrBit::Qubit(id)=>zero.qubits[id.0 as usize],QubitOrBit::Bit(id)=>zero.bits[id.0 as usize]}).collect();
  let wrong=output.iter().zip(&expected).zip(&known).fold(0u64,|acc,((v,e),k)|acc|((v^e)&k&active));if !placeholder{wrong_count+=wrong.count_ones()as usize;}
  for seed in 0..8{
   let mut mr=validation_random(seed);let mut sim=Simulator::new(nq as usize,nb as usize,&mut mr);
   for(lane,row)in data.iter().enumerate(){for(reg,value)in regs[..4].iter().zip(&row[..4]){sim.set_register(reg,*value,lane);}}
   sim.apply_iter(ops.iter());
   for(index,w)in regs[..2].iter().flatten().enumerate(){let v=match w{QubitOrBit::Qubit(id)=>sim.qubits[id.0 as usize],QubitOrBit::Bit(id)=>sim.bits[id.0 as usize]};assert_eq!((v^output[index])&known[index]&active,0,"candidate physicalMR vs ORIGINAL zeroMR known bit{index} batch{batches} seed{seed}");}
   if !placeholder{for lane in 0..data.len(){if wrong>>lane&1!=0{assert!(sim.get_register(&regs[0],lane)!=data[lane][4]||sim.get_register(&regs[1],lane)!=data[lane][5]);}}}
  }
  batches+=1;
 }
 println!("{}",serde_json::json!({"status":"CANDIDATE_KNOWN_COORDINATES_MATCH_ORIGINAL_ZEROMR_EMPIRICAL_SUPPLEMENT_TO_UNIVERSAL_TRANSFER","candidate_stream":args[1],"original_zeroMR_stream":args[4],"mask_program":args[2],"fixture":args[3],"shots":rows.len(),"batches":batches,"independent_candidate_physical_mr_streams":8,"known_scored_bits":knownbits,"certified_wrong_value_shots":if placeholder{serde_json::Value::Null}else{serde_json::json!(wrong_count)},"candidate_protected_vs_original_zeroMR_known_bit_containment_passed":true,"seconds":timer.elapsed().as_secs_f64()}));
}
