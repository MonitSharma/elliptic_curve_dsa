"""Observation only: snapshot the original builder vector and real square R0 wire map."""
from pathlib import Path
import sys
source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
builder=Path(sys.argv[3]).read_text()
needle='        std::mem::take(&mut self.ops)'
writer='''        {
            use std::io::Write;
            let path = "/home/hclau/ecdsa_research/overnight-20261014/product-evidence/raw-handoff/raw-ops.bin";
            let mut w = std::io::BufWriter::new(std::fs::File::create(path).unwrap());
            w.write_all(b"QECCOPSZ").unwrap();
            w.write_all(&(self.ops.len() as u64).to_le_bytes()).unwrap();
            let mut enc = zstd::stream::write::Encoder::new(w, 3).unwrap();
            for op in &self.ops {
                let mut rec=[0u8;56];
                rec[..4].copy_from_slice(&(op.kind as u32).to_le_bytes());
                for (j,v) in [op.q_control2.0,op.q_control1.0,op.q_target.0,op.c_target.0,op.c_condition.0,op.r_target.0].iter().enumerate() {
                    rec[8+j*8..16+j*8].copy_from_slice(&v.to_le_bytes());
                }
                enc.write_all(&rec).unwrap();
            }
            enc.finish().unwrap().flush().unwrap();
            eprintln!("RAW_OPS_SNAPSHOT ops={} path={path}", self.ops.len());
        }
'''+needle
assert builder.count(needle)==1
out.joinpath('builder.rs').write_text(builder.replace(needle,writer),newline='\n')
leap=source.joinpath('leapfrog.rs').read_text();needle='    T6_PRESEED.with(|s| *s.borrow_mut() = Some(r0));'
assert leap.count(needle)==1
new='''    eprintln!("SQUARE_R0_WIRES {:?}", r0.iter().map(|q|q.0).collect::<Vec<_>>());
    eprintln!("HANDOFF_SETTINGS native_sfuse_b={} t6_seedfuse={} seam_fs={} erase_compare={}",
        super::native_sfuse_b::mode(), t6_seedfuse(), fs, k);
'''+needle
out.joinpath('leapfrog.rs').write_text(leap.replace(needle,new),newline='\n')
