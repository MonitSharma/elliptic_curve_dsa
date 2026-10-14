from pathlib import Path
import sys
folder=Path(__file__).parent;out=folder/'full-cross-source';out.mkdir(exist_ok=True)
s=(folder/'zero-test-source/square.rs').read_bytes()
needle=b'    let acc=match super::optional_env::<usize>("SQ_ASM_TAIL"){Some(e)=>&full[..full.len().min(cross.len()+e)],None=>full};'
assert s.count(needle)==1
replacement=b'''    // Focused diagnostic: retain the exact entire assembly carry path.
    eprintln!("FULL_CROSS inverse={} cross={} full={} installed_e={:?}", inverse, cross.len(), full.len(), super::optional_env::<usize>("SQ_ASM_TAIL"));
    let acc=full;'''
out.joinpath('square.rs').write_bytes(s.replace(needle,replacement))
s=(folder/'raw-handoff-source/builder.rs').read_text().replace('/product-evidence/raw-handoff/raw-ops.bin','/product-evidence/full-cross/raw-ops.bin')
out.joinpath('builder.rs').write_text(s,newline='\n')
