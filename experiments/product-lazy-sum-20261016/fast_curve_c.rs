// Isolated public-input preparation. Both full and split APIs are hash bound.
use std::ffi::{CString,c_void,c_char,c_int};
#[link(name="dl")]unsafe extern "C"{fn dlopen(path:*const c_char,flags:c_int)->*mut c_void;fn dlsym(handle:*mut c_void,name:*const c_char)->*mut c_void;fn dlerror()->*const c_char;}
type PairFunction=unsafe extern "C" fn(u32,*const u8,*mut u8)->c_int;
struct CBackend{pairs:PairFunction,inputs:Option<PairFunction>,adds:Option<PairFunction>}
static C_BACKEND:std::sync::OnceLock<CBackend>=std::sync::OnceLock::new();
struct FastCurveC;
impl FastCurveC{
 fn new(window:usize)->Self{C_BACKEND.get_or_init(||unsafe{
  let split=std::env::var_os("DEFER_EXPECTED_SUMS").is_some();
  let(path,sha)=if split{("/home/hclau/ecdsa_research/prefilter-20261015/scalar-split-v1/libscalar_split.so","365407f4d6922f4cedeaa23c896d4f3ffd53b264dbfa9689bea774988e52695d")}else{("/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so","3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f")};
  sha_check(path,sha);let path=CString::new(path).unwrap();let handle=dlopen(path.as_ptr(),2);assert!(!handle.is_null());
  let init=dlsym(handle,b"scalar_fast_fixed_init\0".as_ptr().cast());let pairs=dlsym(handle,b"scalar_fast_pairs\0".as_ptr().cast());assert!(!init.is_null()&&!pairs.is_null());let init:unsafe extern "C" fn(u32)->c_int=std::mem::transmute(init);assert_ne!(init(window as u32),0);
  let(mut inputs,mut adds)=(None,None);if split{let i=dlsym(handle,b"scalar_fast_inputs\0".as_ptr().cast());let a=dlsym(handle,b"scalar_fast_add_pairs\0".as_ptr().cast());assert!(!i.is_null()&&!a.is_null());inputs=Some(std::mem::transmute::<*mut c_void,PairFunction>(i));adds=Some(std::mem::transmute::<*mut c_void,PairFunction>(a));}
  CBackend{pairs:std::mem::transmute::<*mut c_void,PairFunction>(pairs),inputs,adds}
 });Self}
 fn deferred(&self)->bool{C_BACKEND.get().unwrap().inputs.is_some()}
 fn prepare(&self,scalars:&[U256],defer:bool)->Vec<((U256,U256),(U256,U256),(U256,U256))>{
  assert!(scalars.len()%2==0&&scalars.len()<=128);let count=scalars.len()/2;let mut input=Vec::with_capacity(scalars.len()*32);for scalar in scalars{input.extend_from_slice(&scalar.to_be_bytes::<32>());}let mut output=vec![0u8;count*192];let backend=C_BACKEND.get().unwrap();let function=if defer{backend.inputs.unwrap()}else{backend.pairs};assert_ne!(unsafe{function(count as u32,input.as_ptr(),output.as_mut_ptr())},0);
  output.chunks_exact(192).map(|row|{let point=|off|(U256::from_be_slice(&row[off..off+32]),U256::from_be_slice(&row[off+32..off+64]));(point(0),point(64),point(128))}).collect()
 }
 fn points_with_sums(&self,scalars:&[U256])->Vec<((U256,U256),(U256,U256),(U256,U256))>{self.prepare(scalars,false)}
 fn expected_points(&self,points:&[PointTriple])->Vec<(U256,U256)>{
  assert!(!points.is_empty()&&points.len()<=64);let mut input=Vec::with_capacity(points.len()*128);for(t,o,_)in points{for value in [t.0,t.1,o.0,o.1]{input.extend_from_slice(&value.to_be_bytes::<32>());}}
  let mut output=vec![0u8;points.len()*64];let function=C_BACKEND.get().unwrap().adds.unwrap();assert_ne!(unsafe{function(points.len()as u32,input.as_ptr(),output.as_mut_ptr())},0);output.chunks_exact(64).map(|row|(U256::from_be_slice(&row[..32]),U256::from_be_slice(&row[32..]))).collect()
 }
}
