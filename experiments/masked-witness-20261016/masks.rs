#[repr(C)]#[derive(Clone,Copy)]struct MaskNode{kind:u32,a:u32,b:u32,aux:u32}
type MaskRun=unsafe extern "C" fn(*const MaskNode,usize,*const u64,usize,*mut u64,usize,*const u32,usize,*mut u64)->i32;
struct MaskProgram{nodes:Vec<MaskNode>,roots:Vec<u32>,workspace:Mutex<Vec<u64>>,run:MaskRun}
static MASK_PROGRAM:std::sync::OnceLock<MaskProgram>=std::sync::OnceLock::new();
fn mask_program()->&'static MaskProgram{MASK_PROGRAM.get_or_init(||{
 let path=std::env::var("MASK_DAG_PATH").expect("frozen mask export path required");let hash=std::env::var("MASK_DAG_SHA256").expect("frozen mask export hash required");sha_check(&path,&hash);
 let data=std::fs::read(path).unwrap();assert_eq!(&data[..8],b"MRMASK01");let u64at=|i|u64::from_le_bytes(data[i..i+8].try_into().unwrap());let n=u64at(8)as usize;assert!(n>0&&n<=40_000_000,"bounded mask evaluator capacity");assert_eq!(u64at(16),1024);assert_eq!(u64at(24),512);assert_eq!(data.len(),32+n*16+512*4);
 let mut nodes=Vec::with_capacity(n);for(i,r)in data[32..32+n*16].chunks_exact(16).enumerate(){let f=|j|u32::from_le_bytes(r[j..j+4].try_into().unwrap());let o=MaskNode{kind:f(0),a:f(4),b:f(8),aux:f(12)};assert_eq!(o.aux,0);assert!(o.kind<=5);if o.kind==2{assert!(o.a<1024);}if o.kind>=3{assert!((o.a as usize)<i&&(o.b as usize)<i);}nodes.push(o);}
 let roots=data[32+n*16..].chunks_exact(4).map(|r|u32::from_le_bytes(r.try_into().unwrap())).collect::<Vec<_>>();assert!(roots.iter().all(|r|(*r as usize)<n));drop(data);
 let lib="/home/hclau/ecdsa_research/mask-evaluator-20261016/libmask8.so";sha_check(lib,"641f8c1b6578c9878244650bd05cbbbd1fd452e9199c504bc76832cf72fd81e1");let run=unsafe{let s=CString::new(lib).unwrap();let h=dlopen(s.as_ptr(),2);assert!(!h.is_null());let f=dlsym(h,b"mask8_eval\0".as_ptr().cast());assert!(!f.is_null());std::mem::transmute::<*mut c_void,MaskRun>(f)};
 eprintln!("MASK_PROGRAM nodes={n} bytes_values={} hash={hash} authoritative_gate=false",n*64);
 MaskProgram{nodes,roots,workspace:Mutex::new(vec![0u64;n*8]),run}
})}
fn known_masks(points:&[PointTriple])->Vec<u64>{
 let p=mask_program();let mut ports=vec![0u64;1024*8];for(index,(t,o,_))in points.iter().enumerate(){let(j,lane)=(index/64,index%64);for(reg,value)in [t.0,t.1,o.0,o.1].iter().enumerate(){for bit in 0..256{ports[(reg*256+bit)*8+j]|=(value.bit(bit)as u64)<<lane;}}}
 let mut values=p.workspace.lock().unwrap();let mut out=vec![0u64;512*8];assert_eq!(unsafe{(p.run)(p.nodes.as_ptr(),p.nodes.len(),ports.as_ptr(),1024,values.as_mut_ptr(),p.nodes.len(),p.roots.as_ptr(),512,out.as_mut_ptr())},0);for word in &mut out{*word=!*word;}out
}
