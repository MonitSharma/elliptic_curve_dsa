"""Build an external fixed-packet replay against the original protected library."""
from pathlib import Path
root=Path(__file__).resolve().parent
old=Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-replay')
dest=root/'fixed-replay'
assert not dest.exists()
(dest/'src').mkdir(parents=True)
prefix=(old/'src/main.rs').read_text().split('fn main() {')[0]
(dest/'src/main.rs').write_text(prefix+(root/'fixed_replay.rs').read_text())
(dest/'Cargo.toml').write_bytes((old/'Cargo.toml').read_bytes())
(dest/'rust-toolchain').write_bytes((old/'rust-toolchain').read_bytes() if (old/'rust-toolchain').exists() else (root/'diagnostic-b3/rust-toolchain').read_bytes())
