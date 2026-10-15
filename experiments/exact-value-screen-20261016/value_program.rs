type ValueRun=unsafe extern "C" fn(*const CompactOp,usize,*mut u64,*mut u64,*const u64,usize,*mut u64,usize,*mut usize)->i32;
static VALUE_RUN:std::sync::OnceLock<ValueRun>=std::sync::OnceLock::new();
fn value_backend()->ValueRun{*VALUE_RUN.get_or_init(||unsafe{let path=CString::new("/home/hclau/ecdsa_research/exact-value-screen-20261016/libvalue8.so").unwrap();let h=dlopen(path.as_ptr(),2);assert!(!h.is_null());let p=dlsym(h,b"value8_run\0".as_ptr().cast());assert!(!p.is_null());std::mem::transmute::<*mut c_void,ValueRun>(p)})}
fn check_sha256(path:&str,expected:&str){let output=std::process::Command::new("sha256sum").arg(path).output().unwrap();assert!(output.status.success());let s=String::from_utf8(output.stdout).unwrap();assert_eq!(s.split_whitespace().next().unwrap(),expected,"frozen input binding {path}");}
static VALUE_INPUT_BITS:std::sync::OnceLock<Vec<usize>>=std::sync::OnceLock::new();
fn bind_value_source(path:&str,regs:&[Vec<QubitOrBit>]){check_sha256(path,"2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e");assert!(VALUE_INPUT_BITS.set(regs.iter().take(4).flatten().filter_map(|w|if let QubitOrBit::Bit(id)=w{Some(id.0 as usize)}else{None}).collect()).is_ok());}
fn tr_and(a:u8,b:u8)->u8{if a==0||b==0{0}else if a==1&&b==1{1}else{2}}
fn tr_or(a:u8,b:u8)->u8{if a==1||b==1{1}else if a==0&&b==0{0}else{2}}
fn tr_not(a:u8)->u8{if a==2{2}else{1-a}}
fn tr_xor(a:u8,b:u8)->u8{if a==2||b==2{2}else{a^b}}
fn simplify_value(p:Compact)->Compact{
 let mut bits=vec![0u8;45701];let mut base=1;let mut stack=Vec::new();let mut out=Vec::new();
 for id in VALUE_INPUT_BITS.get().unwrap(){bits[*id]=2;}
 for raw in p.ops{let mut o=raw;let guard=if o.c==u32::MAX{1}else{bits[o.c as usize]};let c=tr_and(base,guard);
  match o.k{15=>{stack.push(base);base=tr_and(base,bits[o.c as usize]);out.push(o);continue;},16=>{base=stack.pop().unwrap();out.push(o);continue;},
   3=>bits[o.bt as usize]=tr_xor(bits[o.bt as usize],c),4=>bits[o.bt as usize]=tr_and(bits[o.bt as usize],tr_not(c)),5=>bits[o.bt as usize]=tr_or(bits[o.bt as usize],c),
   12=>bits[o.bt as usize]=tr_or(tr_and(bits[o.bt as usize],tr_not(c)),tr_and(2,c)),_=>{}}
  if matches!(o.k,0|7|9|14){continue;}
  if c==0{if matches!(o.k,11|12){o.k=18;out.push(o);}continue;}
  if guard==1{o.c=u32::MAX;}out.push(o);
 }assert!(stack.is_empty());eprintln!("EXACT_VALUE_SIMPLIFIED ops={} rng_words={} phase_excluded=true",out.len(),p.rng_count);Compact{ops:out,rng_count:p.rng_count}
}
static VALUE_PROGRAM:std::sync::OnceLock<Compact>=std::sync::OnceLock::new();
fn value_program()->&'static Compact{VALUE_PROGRAM.get_or_init(||{
 let path="/home/hclau/ecdsa_research/prefilter-20261015/evidence/certified-reduced-tip.compact16.bin";
 check_sha256(path,"a4d01570c76b589ed5d2d59b79ac12ccb4a7a155f1f70d415e3c5da2e5935927");
 let bytes=std::fs::read(path).unwrap();assert_eq!(bytes.len(),161794160);let mut ops=Vec::new();let mut rng_count=0;
 for r in bytes.chunks_exact(16){let o=CompactOp{a:u16::from_le_bytes(r[0..2].try_into().unwrap()),b:u16::from_le_bytes(r[2..4].try_into().unwrap()),t:u16::from_le_bytes(r[4..6].try_into().unwrap()),k:r[6],pad:r[7],c:u32::from_le_bytes(r[8..12].try_into().unwrap()),bt:u32::from_le_bytes(r[12..16].try_into().unwrap())};assert_eq!(o.pad,0);if matches!(o.k,11|12){rng_count+=1;}ops.push(o);}
 assert_eq!(rng_count,906156);simplify_value(Compact{ops,rng_count})
})}
