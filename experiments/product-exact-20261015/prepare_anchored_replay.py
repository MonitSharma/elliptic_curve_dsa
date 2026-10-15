from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
dest=root/'anchored-replay'
shutil.copytree(root/'flags-replay',dest,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
path=dest/'src/main.rs';text=path.read_text()
old='''        for &old in &map{let mut b=[0u8;8];if mode=="candidate"{XofReader::read(&mut xof,&mut b);}else{XofReader::read(&mut independent,&mut b);}let v=u64::from_le_bytes(b);rw.push(v);if old!=usize::MAX{lw[old]=v;}}'''
new='''        if mode=="candidate" {
            // Preserve official sequential RNG consumption in candidate mode.
            for &old in &map{let mut b=[0u8;8];XofReader::read(&mut xof,&mut b);let v=u64::from_le_bytes(b);rw.push(v);if old!=usize::MAX{lw[old]=v;}}
        } else {
            // Anchor every original measurement to its immutable ordinal.
            // Added cache events draw from a disjoint reproducible stream.
            for word in &mut lw {let mut b=[0u8;8];XofReader::read(&mut independent,&mut b);*word=u64::from_le_bytes(b);}
            let mut fresh_seed=Shake256::default();fresh_seed.update(b"product-b3-paired-added-cache-measurement-v1");fresh_seed.update(&(batch as u64).to_le_bytes());let mut fresh=fresh_seed.finalize_xof();
            for &old in &map {if old==usize::MAX {let mut b=[0u8;8];XofReader::read(&mut fresh,&mut b);rw.push(u64::from_le_bytes(b));}else{rw.push(lw[old]);}}
            println!("ANCHORED_ORIGINAL_MR batch={batch} events={nold} first={:?}",&lw[..lw.len().min(3)]);
        }'''
assert text.count(old)==1
path.write_text(text.replace(old,new))
