"""Source-bound true production replay, retaining fixed point families and batch-specific MR domains."""
from pathlib import Path
import subprocess,sys
folder=Path(__file__).parent;base=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve()
subprocess.run([sys.executable,str(folder/'create-producer-replay.py'),str(base),str(dest)],check=True)
s=dest.joinpath('src/main.rs').read_text()
needle='let ops=load_ops(&a[1]).unwrap();';assert s.count(needle)==1
s=s.replace(needle,'let batch:usize=a.get(6).map(|s|s.parse().unwrap()).unwrap_or(0);println!("PRODUCTION_REPLAY batch={batch} packet={} stream={} score=NONE",a[2],a[1]);'+needle)
needle=".filter(|s|!s.starts_with('#')).take(64)";assert s.count(needle)==1;s=s.replace(needle,".filter(|s|!s.starts_with('#')).skip(batch*64).take(64)")
needle='h.update(&0u64.to_le_bytes());';assert s.count(needle)==1;s=s.replace(needle,'h.update(&(batch as u64).to_le_bytes());')
dest.joinpath('src/main.rs').write_text(s,newline='\n')
t=dest.joinpath('Cargo.toml').read_text().replace('name="product_producer_replay"','name="product_positive_production_replay"')
dest.joinpath('Cargo.toml').write_text(t,newline='\n')
