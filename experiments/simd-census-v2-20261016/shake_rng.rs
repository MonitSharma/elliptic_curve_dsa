// Exact eight-way census XOF with per-lane offsets after all accepted scalars.
type Create=unsafe extern "C" fn()->*mut c_void;
type AbsorbSame=unsafe extern "C" fn(*mut c_void,*const u8,usize)->c_int;
type Absorb8=unsafe extern "C" fn(*mut c_void,*const u8,usize,usize)->c_int;
type Finalize=unsafe extern "C" fn(*mut c_void)->c_int;
type Select=unsafe extern "C" fn(*mut c_void,*const usize,*mut u64,usize)->c_int;
type Free=unsafe extern "C" fn(*mut c_void);
struct ShakeBackend{create:Create,same:AbsorbSame,eight:Absorb8,finalize:Finalize,select:Select,free:Free}
static SHAKE_BACKEND:std::sync::OnceLock<ShakeBackend>=std::sync::OnceLock::new();
fn shake_backend()->&'static ShakeBackend{SHAKE_BACKEND.get_or_init(||unsafe{
 let path=CString::new("/home/hclau/ecdsa_research/shake8-20261015/libshake8.so").unwrap();let h=dlopen(path.as_ptr(),2);assert!(!h.is_null());
 let symbol=|name:&[u8]|{let p=dlsym(h,name.as_ptr().cast());assert!(!p.is_null());p};
 ShakeBackend{create:std::mem::transmute::<*mut c_void,Create>(symbol(b"shake8_create\0")),same:std::mem::transmute::<*mut c_void,AbsorbSame>(symbol(b"shake8_absorb_same\0")),eight:std::mem::transmute::<*mut c_void,Absorb8>(symbol(b"shake8_absorb8\0")),finalize:std::mem::transmute::<*mut c_void,Finalize>(symbol(b"shake8_finalize\0")),select:std::mem::transmute::<*mut c_void,Select>(symbol(b"shake8_select_words8\0")),free:std::mem::transmute::<*mut c_void,Free>(symbol(b"shake8_free\0"))}
})}
fn rng8(label:&str,batches:&[Batch],words:usize,out:&mut[u64]){
 assert_eq!(batches.len(),8);assert_eq!(out.len(),words*8);let backend=shake_backend();
 let indices=batches.iter().flat_map(|b|b.index.to_le_bytes()).collect::<Vec<_>>();let offsets=batches.iter().map(|b|(64+b.skipped as usize)*8).collect::<Vec<_>>();
 unsafe{let state=(backend.create)();assert!(!state.is_null());for data in [CENSUS_DOMAIN,&(label.len()as u64).to_le_bytes(),label.as_bytes()]{assert_eq!((backend.same)(state,data.as_ptr(),data.len()),0);}assert_eq!((backend.eight)(state,indices.as_ptr(),8,8),0);assert_eq!((backend.finalize)(state),0);assert_eq!((backend.select)(state,offsets.as_ptr(),out.as_mut_ptr(),words),0);(backend.free)(state);}
}
