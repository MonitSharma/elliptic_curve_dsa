from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'packed-stream-20261016';tool=root/'tool';(tool/'src').mkdir(parents=True,exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
for path in (old/'tool/src').glob('*.rs'):shutil.copyfile(path,tool/'src'/path.name)
source=(old/'generated-packed_body.rs').read_text();source='include!("masks.rs");\n'+source
needle='points.iter().enumerate().map(|(index,(_,_,expected))|'
assert source.count(needle)==1;source=source.replace(needle,'let known=known_masks(points);\n '+needle)
needle='for(reg,value)in regs[..2].iter().zip([expected.0,expected.1]){for(i,wire)in reg.iter().enumerate(){let raw=match wire{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j],QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]};wrong|=((raw>>lane)&1)!=(value.bit(i)as u64);}}wrong}'
replacement='for(outreg,(reg,value))in regs[..2].iter().zip([expected.0,expected.1]).enumerate(){for(i,wire)in reg.iter().enumerate(){let raw=match wire{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j],QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]};wrong|=((raw>>lane)&1)!=(value.bit(i)as u64)&&((known[(outreg*256+i)*8+j]>>lane)&1)!=0;}}wrong}'
assert source.count(needle)==1;source=source.replace(needle,replacement)
# Keep this first integration benchmark hard-gated false and bounded.
source=source.replace('let program=zero_program();','let program=zero_program();mask_program();',1)
(root/'generated-masked_body.rs').write_text(source);(tool/'src/packed_body.rs').write_text(source);shutil.copyfile(root/'masks.rs',tool/'src/masks.rs')
rail=(tool/'src/rail_fast_ffi.rs').read_text().replace('/home/hclau/ecdsa_research/simd-rails-20261015/librail8.so','/home/hclau/ecdsa_research/rail-masks-20261016/librail8_masks.so')
(tool/'src/rail_fast_ffi.rs').write_text(rail)
