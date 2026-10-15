// Public-input variable-time fixed-base secp256k1 multiplication. This is an
// external research accelerator, never part of a submission or protected files.
use k256::{AffinePoint,ProjectivePoint};
use k256::elliptic_curve::{group::Curve,sec1::ToEncodedPoint};
struct FastCurve { table: Vec<Vec<AffinePoint>>, window:usize }
impl FastCurve {
 fn new(window:usize)->Self {
  assert!((4..=16).contains(&window));
  let mut table=Vec::new();let mut base=ProjectivePoint::GENERATOR;
  for _ in 0..(256+window-1)/window {
   let mut projective=vec![ProjectivePoint::IDENTITY;1<<window];
   for j in 1..1<<window {projective[j]=projective[j-1]+base;}
   let mut affine=vec![AffinePoint::IDENTITY;1<<window];
   <ProjectivePoint as Curve>::batch_normalize(&projective,&mut affine);
   table.push(affine);
   for _ in 0..window {base=base.double();}
  }
  Self{table,window}
 }
 fn mul_projective(&self,k:U256)->ProjectivePoint {
  let bytes=k.to_le_bytes::<32>();let mut p=ProjectivePoint::IDENTITY;
  for(i,t)in self.table.iter().enumerate(){let off=i*self.window;let mut n=0usize;for j in 0..self.window {if off+j<256 {n|=(((bytes[(off+j)/8]>>((off+j)%8))&1)as usize)<<j;}}if n>0 {p+=t[n];}}
  p
 }
 fn points(&self,ks:&[U256])->Vec<(U256,U256)> {
  let p:Vec<_>=ks.iter().map(|k|self.mul_projective(*k)).collect();
  let mut a=vec![AffinePoint::IDENTITY;p.len()];<ProjectivePoint as Curve>::batch_normalize(&p,&mut a);
  a.iter().map(|p| {let e=p.to_encoded_point(false);if e.as_bytes().len()==1 {(U256::ZERO,U256::ZERO)}else{(U256::from_be_slice(e.x().unwrap()),U256::from_be_slice(e.y().unwrap()))}}).collect()
 }
}
fn fast_curve_test(window:usize) {
 let t=std::time::Instant::now();let fast=FastCurve::new(window);let init=t.elapsed().as_secs_f64();
 let mut h=Shake256::default();h.update(b"prefilter-fastcurve-independent-v1");let mut rng=h.finalize_xof();let mut ks=vec![U256::ZERO,U256::from(1),secp256k1().order,secp256k1().order+U256::from(1),U256::MAX];
 for _ in 0..4096 {let mut r=[0u8;32];XofReader::read(&mut rng,&mut r);ks.push(U256::from_le_bytes(r));}
 let t=std::time::Instant::now();let points=fast.points(&ks);let elapsed=t.elapsed().as_secs_f64();let curve=secp256k1();
 let t=std::time::Instant::now();for(i,k)in ks.iter().enumerate(){assert_eq!(points[i],curve.mul(curve.gx,curve.gy,*k),"fast curve disagrees at scalar {i}");}let reference=t.elapsed().as_secs_f64();
 println!("{{\"kind\":\"fastcurve\",\"window\":{window},\"scalars\":{},\"init_seconds\":{init:.6},\"microseconds_per_scalar\":{:.3},\"reference_microseconds_per_scalar\":{:.3},\"exact_matches\":{}}}",ks.len(),elapsed*1e6/ks.len()as f64,reference*1e6/ks.len()as f64,ks.len());
}
