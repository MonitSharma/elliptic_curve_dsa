// Representation-only evaluator. All roots remain raw discrepancy G; safe=!G.
#[repr(C)]#[derive(Clone,Copy)]struct GuardFusedOp{kind:u32,a:u32,b:u32,packed:u32}
type GuardFusedRun=unsafe extern "C" fn(*const GuardFusedOp,usize,usize,*const u64,usize,*mut u64,usize,*const u32,usize,u32,*mut u64)->i32;
struct GuardFusedProgram{ops:Vec<GuardFusedOp>,slots:usize,roots:Vec<u32>,workspace:Mutex<Vec<u64>>,run:GuardFusedRun}
static GUARD_FUSED_PROGRAM:std::sync::OnceLock<GuardFusedProgram>=std::sync::OnceLock::new();
fn guard_fused_program()->&'static GuardFusedProgram{GUARD_FUSED_PROGRAM.get_or_init(||{
 let root="/home/hclau/ecdsa_research/guard-fused-20261016";
 for(name,sha)in[
  ("guard512.bin","5477d190d11716b0769d0d1c681b49368549345e095a71c85fae871e48e14375"),
  ("COMPILATION-LINEAGE.json","8c7efbddc0bb2d46f3e6a696f53ff677025b066219b3726e84ba12d47e5e070b"),
  ("guard-fused.nodeids-u32le.bin","60f66061b25cc6b1a4ef7fb4873e0bc77eb84c1017ce53bdb0068fed79d1a91b"),
  ("compile-mask-fused.py","3e7026326948afd2ebd3df7c924e09fe20ff6744e972f24d044f33f52774b505"),
  ("verify-mask-fused.py","4c26cccb620c0787ee57d2422a91891c8eb9a2b1468990b29a6f422bee233801")]{sha_check(&format!("{root}/{name}"),sha);}
 let path=format!("{root}/guard-fused.bin");sha_check(&path,"e889e0a6f123a7ae34a9d81339a209ba93aad5246b224057107de3360a9c578a");
 let data=std::fs::read(path).unwrap();assert_eq!(&data[..8],b"MRSLOT02");
 assert_eq!(data[8..40].iter().map(|b|format!("{b:02x}")).collect::<String>(),"5477d190d11716b0769d0d1c681b49368549345e095a71c85fae871e48e14375");
 let word=|i|u64::from_le_bytes(data[i..i+8].try_into().unwrap())as usize;
 let n=word(40);let slots=word(48);assert_eq!((n,slots,word(56),word(64)),(1_130_985,1656,1024,512));assert!(slots<65536);assert_eq!(data.len(),72+n*16+512*4);
 let mut ops=Vec::with_capacity(n);for r in data[72..72+n*16].chunks_exact(16){let w=|j|u32::from_le_bytes(r[j..j+4].try_into().unwrap());let o=GuardFusedOp{kind:w(0),a:w(4),b:w(8),packed:w(12)};assert!(o.kind<=14);let dst=if o.kind>=6{o.packed&65535}else{o.packed};assert!((dst as usize)<slots);if o.kind==2{assert!(o.a<1024);}if o.kind>=3{assert!((o.a as usize)<slots&&(o.b as usize)<slots);}if o.kind>=6{assert!(((o.packed>>16)as usize)<slots);}ops.push(o);}
 let roots=data[72+n*16..].chunks_exact(4).map(|r|u32::from_le_bytes(r.try_into().unwrap())).collect::<Vec<_>>();assert!(roots.iter().all(|r|(*r as usize)<slots));assert!(roots.iter().all(|r|*r==roots[0]));
 let lib="/home/hclau/ecdsa_research/prefilter-20261015/libmask_fused.so";sha_check(lib,"dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0");
 let run=unsafe{let s=CString::new(lib).unwrap();let h=dlopen(s.as_ptr(),2);assert!(!h.is_null());let p=dlsym(h,b"mask_fused_eval\0".as_ptr().cast());assert!(!p.is_null());std::mem::transmute::<*mut c_void,GuardFusedRun>(p)};
 eprintln!("FUSED_GUARD_LINEAGE_BOUND original355f wrapper5477 planE889 slots1656 kernelDc8219 authority=false");
 GuardFusedProgram{ops,slots,roots,workspace:Mutex::new(vec![0;slots*8]),run}
})}
fn guard_safe_fused(points:&[PointTriple])->Vec<bool>{
 assert!(points.len()<=512);if points.is_empty(){return Vec::new();}let p=guard_fused_program();let mut ports=vec![0u64;1024*8];
 for(index,(t,o,_))in points.iter().enumerate(){let(j,lane)=(index/64,index%64);for(reg,v)in[t.0,t.1,o.0,o.1].iter().enumerate(){for bit in 0..256{ports[(reg*256+bit)*8+j]|=(v.bit(bit)as u64)<<lane;}}}
 let mut values=p.workspace.lock().unwrap();let mut out=vec![0u64;512*8];
 // Fixed eight-word mode won the frozen component test; no adaptive-width change.
 assert_eq!(unsafe{(p.run)(p.ops.as_ptr(),p.ops.len(),p.slots,ports.as_ptr(),1024,values.as_mut_ptr(),values.len(),p.roots.as_ptr(),512,8,out.as_mut_ptr())},0);
 assert!(out.chunks_exact(8).all(|row|row==&out[..8]));
 (0..points.len()).map(|i|out[i/64]>>(i%64)&1==0).collect()
}
fn guard_safe(points:&[PointTriple])->Vec<bool>{
 let fused=std::env::var_os("FUSED_GUARD").is_some();
 let result=if fused{guard_safe_fused(points)}else{guard_safe_raw(points)};
 if std::env::var_os("FUSED_GUARD_SHADOW").is_some(){let other=if fused{guard_safe_raw(points)}else{guard_safe_fused(points)};assert_eq!(result,other,"raw/fused G polarity or packed input mismatch");}
 result
}
fn validate_guard_components(){
 let path="/home/hclau/ecdsa_research/prefilter-20261015/a29-conditional-coverage-v1/fixed445-inputs.tsv";sha_check(path,"f958e8665b8d9c7af59e848bddd4864e9fe951db3a835832933d6418cae4a922");
 let mut points=Vec::new();for(i,line)in std::fs::read_to_string(path).unwrap().lines().enumerate(){let f=line.split_whitespace().collect::<Vec<_>>();assert_eq!(f.len(),7);assert_eq!(f[0].parse::<usize>().unwrap(),i);let v=f[1..].iter().map(|s|U256::from_str_radix(s,16).unwrap()).collect::<Vec<_>>();points.push(((v[0],v[1]),(v[2],v[3]),(v[4],v[5])));}
 assert_eq!(points.len(),445);for count in[0,1,11,32,63,64,65,128,445]{assert_eq!(guard_safe_raw(&points[..count]),guard_safe_fused(&points[..count]),"partial guard points{count}");}
 let safe=guard_safe_fused(&points);assert_eq!(safe[..431].iter().filter(|v|**v).count(),428);assert!(safe[431..].iter().all(|v|!*v));
 let path="/home/hclau/ecdsa_research/prefilter-20261015/a29-conditional-prefix-v1/audit-input-u64le.bin";sha_check(path,"b5a1e5c690727cd4ca6351152284f49090cca73c7b4be6a6bc3ab69a6b46897f");let data=std::fs::read(path).unwrap();assert_eq!(data.len(),1024*8);
 let words=data.chunks_exact(8).map(|b|u64::from_le_bytes(b.try_into().unwrap())).collect::<Vec<_>>();let mut audit=Vec::new();
 for lane in 0..32{let mut v=[U256::ZERO;4];for reg in 0..4{for bit in 0..256{if words[reg*256+bit]>>lane&1!=0{v[reg]|=U256::from(1)<<bit;}}}audit.push(((v[0],v[1]),(v[2],v[3]),(U256::ZERO,U256::ZERO)));}
 // Expected coordinates are unused: this audit exercises G only.
 assert_eq!(guard_safe_raw(&audit),guard_safe_fused(&audit));assert!(guard_safe_fused(&audit).iter().all(|v|*v));
 eprintln!("FUSED_GUARD_FIXED445_AUDIT32_PARTIAL_POLARITY_PASS rawG1_17 safe428 repair14excluded allrootsrepeated");
}
