#[repr(C)]#[derive(Clone,Copy)]struct FusedOp{kind:u32,a:u32,b:u32,packed:u32}
type MaskRun=unsafe extern "C" fn(*const FusedOp,usize,usize,*const u64,usize,*mut u64,usize,*const u32,usize,u32,*mut u64)->i32;
struct MaskProgram{ops:Vec<FusedOp>,slots:usize,roots:Vec<u32>,workspace:Mutex<Vec<u64>>,run:MaskRun}
static MASK_PROGRAM:std::sync::OnceLock<MaskProgram>=std::sync::OnceLock::new();
fn mask_program()->&'static MaskProgram{MASK_PROGRAM.get_or_init(||{
 let path="/home/hclau/ecdsa_research/prefilter-20261015/evidence/mr-mask-tip-v3-fused.bin";
 sha_check(path,"1ccbbfc4a45b8d359be9ce21eb4640c72bb9bfe9bffb35f5630c0d13da3f2f8a");
 let data=std::fs::read(path).unwrap();assert_eq!(&data[..8],b"MRSLOT02");
 let embedded=data[8..40].iter().map(|b|format!("{b:02x}")).collect::<String>();assert_eq!(embedded,"560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d");
 let word=|i|u64::from_le_bytes(data[i..i+8].try_into().unwrap())as usize;
 let n=word(40);let slots=word(48);assert_eq!(n,4_842_602);assert_eq!(slots,5323);assert_eq!(word(56),1024);assert_eq!(word(64),512);assert_eq!(data.len(),72+n*16+512*4);
 let mut ops=Vec::with_capacity(n);for r in data[72..72+n*16].chunks_exact(16){let f=|i|u32::from_le_bytes(r[i..i+4].try_into().unwrap());let o=FusedOp{kind:f(0),a:f(4),b:f(8),packed:f(12)};assert!(o.kind<=14);let dest=if o.kind>=6{o.packed&65535}else{o.packed};assert!((dest as usize)<slots);if o.kind==2{assert!(o.a<1024);}if o.kind>=3{assert!((o.a as usize)<slots&&(o.b as usize)<slots);}if o.kind>=6{assert!(((o.packed>>16)as usize)<slots);}ops.push(o);}
 let roots=data[72+n*16..].chunks_exact(4).map(|r|u32::from_le_bytes(r.try_into().unwrap())).collect::<Vec<_>>();assert!(roots.iter().all(|r|(*r as usize)<slots));
 let lib="/home/hclau/ecdsa_research/prefilter-20261015/libmask_fused.so";sha_check(lib,"dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0");
 let run=unsafe{let s=CString::new(lib).unwrap();let h=dlopen(s.as_ptr(),2);assert!(!h.is_null());let f=dlsym(h,b"mask_fused_eval\0".as_ptr().cast());assert!(!f.is_null());std::mem::transmute::<*mut c_void,MaskRun>(f)};
 eprintln!("FUSED_MASK_BINDING source560c12d5 plan1ccbbfc4 ops={n} slots={slots} authoritative_gate=false");
 MaskProgram{ops,slots,roots,workspace:Mutex::new(vec![0u64;slots*8]),run}
})}
fn known_masks(points:&[PointTriple])->Vec<u64>{
 assert!(!points.is_empty()&&points.len()<=512);let p=mask_program();let mut ports=vec![0u64;1024*8];for(index,(t,o,_))in points.iter().enumerate(){let(j,lane)=(index/64,index%64);for(reg,value)in [t.0,t.1,o.0,o.1].iter().enumerate(){for bit in 0..256{ports[(reg*256+bit)*8+j]|=(value.bit(bit)as u64)<<lane;}}}
 let mut values=p.workspace.lock().unwrap();let mut out=vec![0u64;512*8];let width=points.len().div_ceil(64);
 assert_eq!(unsafe{(p.run)(p.ops.as_ptr(),p.ops.len(),p.slots,ports.as_ptr(),1024,values.as_mut_ptr(),values.len(),p.roots.as_ptr(),512,width as u32,out.as_mut_ptr())},0);
 for word in &mut out{*word=!*word;}out
}
