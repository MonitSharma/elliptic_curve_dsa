from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'simd-census-20261016'
tool=root/'tool';(tool/'src').mkdir(parents=True,exist_ok=True)
for name in ['Cargo.toml','Cargo.lock','simd8wide.h','simd8count.c','build.rs']:
 shutil.copyfile(old/'tool'/name,tool/name)
for name in ['prefix.rs','fast_sim_wide.rs','fast_curve_c.rs']:
 shutil.copyfile(old/'tool/src'/name,tool/'src'/name)
source=(old/'main.rs').read_text().replace('include!("fast_curve_c.rs");','include!("fast_curve_c.rs");\ninclude!("shake_rng.rs");')
source=source.replace('FastCurveC::new(20);','FastCurveC::new(20);shake_backend();',1)
needle='let mut reader=batch.xof.clone();let mut raw=vec![0u8;p.rng_count*8];XofReader::read(&mut reader,&mut raw);for(i,word)in raw.chunks_exact(8).enumerate(){rng[i*8+j]=u64::from_le_bytes(word.try_into().unwrap());}batches.push(batch);'
assert source.count(needle)==1;source=source.replace(needle,'batches.push(batch);')
needle='let(mut phase,mut toffoli,mut used)='
insertion='''rng8(&label,&batches,p.rng_count,&mut rng);
    if start<verify_first{let mut expected=vec![0u64;p.rng_count*8];for j in 0..8{let mut reader=batches[j].xof.clone();let mut raw=vec![0u8;p.rng_count*8];XofReader::read(&mut reader,&mut raw);for(i,word)in raw.chunks_exact(8).enumerate(){expected[i*8+j]=u64::from_le_bytes(word.try_into().unwrap());}}assert_eq!(rng,expected,"every measurement word must match protected scalar SHAKE");}
    let(mut phase,mut toffoli,mut used)='''
assert source.count(needle)==1;source=source.replace(needle,insertion)
(tool/'src/main.rs').write_text(source)
shutil.copyfile(root/'shake_rng.rs',tool/'src/shake_rng.rs')
