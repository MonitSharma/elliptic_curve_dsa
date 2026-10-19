mod io;
use sha3::{Digest,Sha3_256};
fn main(){let v=io::load_ops(&std::env::args().nth(1).unwrap());let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}println!("{:x}",h.finalize());}
