from pathlib import Path
root=Path(__file__).resolve().parent
dest=root/'cache-replay/crate';(dest/'src').mkdir(parents=True,exist_ok=True)
old=Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-replay')
source=(old/'src/main.rs').read_text().split('fn main() {')[0]
source=source.replace('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline','/home/hclau/ecdsa_research/product')
(dest/'src/main.rs').write_text(source+(root/'cache_replay.rs').read_text())
manifest=(old/'Cargo.toml').read_text().replace('product_paired_diagnostic','cache_paired_diagnostic').replace('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline','/home/hclau/ecdsa_research/product')
(dest/'Cargo.toml').write_text(manifest)
(dest/'rust-toolchain').write_bytes((old/'rust-toolchain').read_bytes())
