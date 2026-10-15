// Public-input C backend, separately pinned and validated by coordinator.
// Shared initialization completes before screening threads are spawned.
use std::ffi::{CString,c_void,c_char,c_int};
#[link(name="dl")]unsafe extern "C"{fn dlopen(path:*const c_char,flags:c_int)->*mut c_void;fn dlsym(handle:*mut c_void,name:*const c_char)->*mut c_void;fn dlerror()->*const c_char;}
type PairFunction=unsafe extern "C" fn(u32,*const u8,*mut u8)->c_int;
struct CBackend{pairs:PairFunction}
static C_BACKEND:std::sync::OnceLock<CBackend>=std::sync::OnceLock::new();
struct FastCurveC;
impl FastCurveC{
 fn new(window:usize)->Self{C_BACKEND.get_or_init(||unsafe{
  let path=std::env::var("SCALAR_FAST_LIB").unwrap_or_else(|_|"/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so".into());let path=CString::new(path).unwrap();let handle=dlopen(path.as_ptr(),2);if handle.is_null(){let error=dlerror();panic!("Cbackendloadfailed {:?}",std::ffi::CStr::from_ptr(error));}
  let init=dlsym(handle,b"scalar_fast_fixed_init\0".as_ptr().cast());let pairs=dlsym(handle,b"scalar_fast_pairs\0".as_ptr().cast());assert!(!init.is_null()&&!pairs.is_null());let init:unsafe extern "C" fn(u32)->c_int=std::mem::transmute(init);assert_ne!(init(window as u32),0,"Cfixed-baseinitializationfailed");CBackend{pairs:std::mem::transmute::<*mut c_void,PairFunction>(pairs)}
 });Self}
 fn points_with_sums(&self,scalars:&[U256])->Vec<((U256,U256),(U256,U256),(U256,U256))>{assert!(scalars.len()%2==0&&scalars.len()<=128);let count=scalars.len()/2;let mut input=Vec::with_capacity(scalars.len()*32);for scalar in scalars{input.extend_from_slice(&scalar.to_be_bytes::<32>());}let mut output=vec![0u8;count*192];assert_ne!(unsafe{(C_BACKEND.get().unwrap().pairs)(count as u32,input.as_ptr(),output.as_mut_ptr())},0);output.chunks_exact(192).map(|row|{let point=|off| (U256::from_be_slice(&row[off..off+32]),U256::from_be_slice(&row[off+32..off+64]));(point(0),point(64),point(128))}).collect()}
}
