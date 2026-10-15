"""Performance-only shadow copy of the diagnostic model's signed primitives."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
source=root.parent/'prefilter-20261015/tool'
dest=root/'rail-tool'
(dest/'src').mkdir(parents=True,exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:(dest/name).write_bytes((source/name).read_bytes())
s=(source/'src/bin/walk_model.rs').read_text().replace('include!("../walk_native.rs");','include!("walk_native.rs");')
(dest/'src/main.rs').write_text(s)
s=(source/'src/walk_native.rs').read_text()
(root/'original-walk-native.rs').write_text(s)
start=s.index('#[inline(always)]fn ar(')
end=s.index('#[inline(always)]fn pos(',start)
masks=[]
for w in range(257):
 masks.append('['+','.join(str((1<<min(max(w-64*i,0),64))-1)+'u64' for i in range(4))+']')
replacement='const SIGN_MASKS:[[u64;4];257]=['+','.join(masks)+'];\n'+'''
#[inline(always)]fn ar(x:I512,n:usize)->I512 {
 if n==0{return x;}assert!(n<64);let l=x.lo.as_limbs();let high=x.hi as u64;
 I512{lo:U256::from_limbs([(l[0]>>n)|(l[1]<<(64-n)),(l[1]>>n)|(l[2]<<(64-n)),(l[2]>>n)|(l[3]<<(64-n)),(l[3]>>n)|(high<<(64-n))]),hi:x.hi>>n}
}
#[inline(always)]fn sx(x:I512,w:usize)->I512 {
 if w>256{let bits=w-256;let mask=(1i64<<bits)-1;let h=x.hi&mask;return I512{lo:x.lo,hi:if h&(1<<(bits-1))!=0{h|!mask}else{h}};}
 assert!(w>0);let l=x.lo.as_limbs();let mask=SIGN_MASKS[w];let negative=(l[(w-1)/64]>>((w-1)%64))&1;let fill=0u64.wrapping_sub(negative);
 I512{lo:U256::from_limbs([(l[0]&mask[0])|(fill&!mask[0]),(l[1]&mask[1])|(fill&!mask[1]),(l[2]&mask[2])|(fill&!mask[2]),(l[3]&mask[3])|(fill&!mask[3])]),hi:fill as i64}
}
'''
s=s[:start]+replacement+s[end:]
(dest/'src/walk_native.rs').write_text(s)
