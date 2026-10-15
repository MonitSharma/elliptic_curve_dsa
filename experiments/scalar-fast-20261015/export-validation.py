from pathlib import Path
import ctypes
import hashlib
root=Path(__file__).resolve().parent
lib=ctypes.CDLL(str(root/'libscalar_fast_batch.so'))
lib.scalar_fast_fixed_init.argtypes=[ctypes.c_uint]
lib.scalar_fast_pairs.argtypes=[ctypes.c_uint,ctypes.c_void_p,ctypes.c_void_p]
assert lib.scalar_fast_fixed_init(16)==1
count=4096
data=bytearray(hashlib.shake_256(b'scalar-fast-independent-20261015').digest(count*64))
n=int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141',16)
edges=[(0,1),(1,n-1),(n,2),(n+1,3),(2**256-1,n+1),(n-1,n-1),(0,0)]
for i,(a,b) in enumerate(edges):data[64*i:64*i+64]=a.to_bytes(32,'big')+b.to_bytes(32,'big')
with (root/'validation-vectors.tsv').open('w') as f:
 for start in range(0,count,64):
  scalars=bytes(data[start*64:(start+64)*64]);source=ctypes.create_string_buffer(scalars);out=ctypes.create_string_buffer(64*192)
  assert lib.scalar_fast_pairs(64,source,out)==1
  for i in range(64):
   f.write(' '.join([scalars[i*64:i*64+32].hex(),scalars[i*64+32:i*64+64].hex()]+[out.raw[i*192+j*32:i*192+(j+1)*32].hex() for j in range(6)])+'\n')

old=root.parent/'wide-cache-20261015/single-replay'
dest=root/'verify-reference'
(dest/'src').mkdir(parents=True,exist_ok=True)
prefix=(old/'src/main.rs').read_text().split('// Independent reconstruction')[0]
main='''
fn main(){
 let a:Vec<_>=std::env::args().collect();let c=secp256k1();let input=std::fs::read_to_string(&a[1]).unwrap();let mut shots=0;
 for line in input.lines(){let v:Vec<_>=line.split_whitespace().map(|s|U256::from_str_radix(s,16).unwrap()).collect();assert_eq!(v.len(),8);
  let p=c.mul(c.gx,c.gy,v[0]);let q=c.mul(c.gx,c.gy,v[1]);let sum=c.add(p.0,p.1,q.0,q.1);
  assert_eq!([p.0,p.1,q.0,q.1,sum.0,sum.1],v[2..],"reference mismatch at shot {}",shots);shots+=1;
 }
 println!("REFERENCE_VALIDATED shots={shots} scalars={} coordinates={} includes_zero_order_overflow_infinity=true",shots*2,shots*6);
}
'''
(dest/'src/main.rs').write_text(prefix+main)
for name in ['Cargo.toml','Cargo.lock']:(dest/name).write_bytes((old/name).read_bytes())
