// Raw G=1 excludes conditional transfer. This component never enables rejection.
#[repr(C)]#[derive(Clone,Copy)]struct GuardNode{kind:u32,a:u32,b:u32,aux:u32}
type GuardRun=unsafe extern "C" fn(*const GuardNode,usize,*const u64,usize,*mut u64,usize,*const u32,usize,*mut u64)->i32;
struct GuardProgram{nodes:Vec<GuardNode>,root:u32,workspace:Mutex<Vec<u64>>,run:GuardRun}
static GUARD_PROGRAM:std::sync::OnceLock<GuardProgram>=std::sync::OnceLock::new();
fn guard_program()->&'static GuardProgram{GUARD_PROGRAM.get_or_init(||{
 let path="/home/hclau/ecdsa_research/prefilter-20261015/a29-conditional-prefix-v1/public-discrepancy-guard.bin";
 sha_check(path,"355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3");
 let data=std::fs::read(path).unwrap();assert_eq!(&data[..8],b"MRMASK01");
 let word=|i|u64::from_le_bytes(data[i..i+8].try_into().unwrap())as usize;
 let n=word(8);assert_eq!(n,1_831_784);assert_eq!(word(16),1024);assert_eq!(word(24),1);assert_eq!(data.len(),32+n*16+4);
 let mut nodes=Vec::with_capacity(n);
 for(i,r)in data[32..32+n*16].chunks_exact(16).enumerate(){let w=|j|u32::from_le_bytes(r[j..j+4].try_into().unwrap());let o=GuardNode{kind:w(0),a:w(4),b:w(8),aux:w(12)};assert_eq!(o.aux,0);assert!(o.kind<=5);if o.kind==2{assert!(o.a<1024);}if o.kind>=3{assert!((o.a as usize)<i&&(o.b as usize)<i);}nodes.push(o);}
 let root=u32::from_le_bytes(data[32+n*16..].try_into().unwrap());assert!((root as usize)<n);
 let lib="/home/hclau/ecdsa_research/mask-evaluator-20261016/libmask8.so";sha_check(lib,"641f8c1b6578c9878244650bd05cbbbd1fd452e9199c504bc76832cf72fd81e1");
 let run=unsafe{let s=CString::new(lib).unwrap();let h=dlopen(s.as_ptr(),2);assert!(!h.is_null());let p=dlsym(h,b"mask8_eval\0".as_ptr().cast());assert!(!p.is_null());std::mem::transmute::<*mut c_void,GuardRun>(p)};
 GuardProgram{nodes,root,workspace:Mutex::new(vec![0;n*8]),run}
})}
fn guard_safe(points:&[PointTriple])->Vec<bool>{
 assert!(points.len()<=512);if points.is_empty(){return Vec::new();}let p=guard_program();let mut ports=vec![0u64;1024*8];
 for(index,(t,o,_))in points.iter().enumerate(){let(j,lane)=(index/64,index%64);for(reg,v)in[t.0,t.1,o.0,o.1].iter().enumerate(){for bit in 0..256{ports[(reg*256+bit)*8+j]|=(v.bit(bit)as u64)<<lane;}}}
 let mut values=p.workspace.lock().unwrap();let roots=vec![p.root;512];let mut out=vec![0u64;512*8];
 assert_eq!(unsafe{(p.run)(p.nodes.as_ptr(),p.nodes.len(),ports.as_ptr(),1024,values.as_mut_ptr(),p.nodes.len(),roots.as_ptr(),512,out.as_mut_ptr())},0);
 assert!(out.chunks_exact(8).all(|row|row==&out[..8]));
 (0..points.len()).map(|i|out[i/64]>>(i%64)&1==0).collect()
}
fn protected_fallback_kind(ops:&[Op],packet:&mut LazyPacket,regs:&[Vec<QubitOrBit>],nq:usize,nb:usize,curve:&FastCurveC)->(&'static str,usize){
 fill_packet(packet,curve);let mut reader=packet.reader.clone();let mut sim=Simulator::new(nq,nb,&mut reader);let mut shots=0;
 for points in &packet.batches{sim.clear_for_shot();for(lane,(t,o,_))in points.iter().enumerate(){for(reg,v)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){sim.set_register(reg,v,lane);}}sim.apply_iter(ops.iter());shots+=points.len();
  if points.iter().enumerate().any(|(lane,(_,_,expected))|sim.get_register(&regs[0],lane)!=expected.0||sim.get_register(&regs[1],lane)!=expected.1){return("classical",shots);}
  let mask=if points.len()==64{u64::MAX}else{(1u64<<points.len())-1};if sim.phase&mask!=0{return("phase",shots);}
  for reg in regs{for wire in reg{if let QubitOrBit::Qubit(q)=wire{sim.qubits[q.0 as usize]=0;}}}if sim.qubits.iter().any(|v|v&mask!=0){return("ancilla",shots);}
 }("pass",shots)
}
fn validate_fixed_transfer(program:&ZeroProgram,original:&[Op],candidate:&[Op],regs:&[Vec<QubitOrBit>],nq:usize,nb:usize){
 assert_eq!((nq,nb),(1234,66245));
 let path="/home/hclau/ecdsa_research/prefilter-20261015/a29-conditional-coverage-v1/fixed445-inputs.tsv";
 sha_check(path,"f958e8665b8d9c7af59e848bddd4864e9fe951db3a835832933d6418cae4a922");
 let text=std::fs::read_to_string(path).unwrap();let mut points=Vec::new();for(i,line)in text.lines().enumerate(){let fields=line.split_whitespace().collect::<Vec<_>>();assert_eq!(fields.len(),7);assert_eq!(fields[0].parse::<usize>().unwrap(),i);let v=fields[1..].iter().map(|s|U256::from_str_radix(s,16).unwrap()).collect::<Vec<_>>();points.push(((v[0],v[1]),(v[2],v[3]),(v[4],v[5])));}
 assert_eq!(points.len(),445);let safe=guard_safe(&points);assert_eq!(safe[..431].iter().filter(|v|**v).count(),428);assert!(safe[431..].iter().all(|v|!*v));
 let known=known_masks(&points);let wrong=packed_values(program,&points,regs,nq,nb,Some(original));
 assert_eq!(wrong[..431].iter().filter(|v|**v).count(),418);assert!(wrong[431..].iter().all(|v|!*v));
 assert!(wrong.iter().zip(&safe).all(|(wrong,safe)|!*wrong||*safe));
 let mut known_bits_checked=0usize;
 for(group,chunk)in points.chunks(64).enumerate(){let mut rz=ZeroReader;let mut cz=ZeroReader;let mut os=Simulator::new(nq,nb,&mut rz);let mut cs=Simulator::new(nq,nb,&mut cz);
  for(lane,(t,o,_))in chunk.iter().enumerate(){for(reg,v)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){os.set_register(reg,v,lane);cs.set_register(reg,v,lane);}}
  os.apply_iter(original.iter());cs.apply_iter(candidate.iter());
  for(lane,(_,_,expected))in chunk.iter().enumerate(){let index=group*64+lane;if !safe[index]{continue;}if wrong[index]{assert!(cs.get_register(&regs[0],lane)!=expected.0||cs.get_register(&regs[1],lane)!=expected.1,"false provisional witness input{index}");}for(ri,reg)in regs[..2].iter().enumerate(){for(bit,w)in reg.iter().enumerate(){if(known[(ri*256+bit)*8+group]>>lane)&1==0{continue;}let(a,b)=match w{QubitOrBit::Qubit(q)=>(os.qubits[q.0 as usize],cs.qubits[q.0 as usize]),QubitOrBit::Bit(b)=>(os.bits[b.0 as usize],cs.bits[b.0 as usize])};assert_eq!((a>>lane)&1,(b>>lane)&1,"conditional known output differs input{index} reg{ri} bit{bit}");known_bits_checked+=1;}}}
 }
 eprintln!("FIXED445_GUARD_CONDITIONAL_KNOWN_BITS_PASS safe_old428 excluded_old3 excluded_repair14 checked_bits={known_bits_checked}");
}
