from pathlib import Path
import sys
root=Path(__file__).resolve().parent
dest=Path(sys.argv[1]);(dest/'src').mkdir(parents=True,exist_ok=True)
old=Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-replay')
source=(old/'src/main.rs').read_text().split('fn main() {')[0]
(dest/'src/main.rs').write_text(source+(root/'cache_replay.rs').read_text())
(dest/'Cargo.toml').write_bytes((old/'Cargo.toml').read_bytes())
(dest/'rust-toolchain').write_bytes(Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline/rust-toolchain').read_bytes())
