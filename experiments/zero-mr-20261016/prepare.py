from pathlib import Path
root=Path(__file__).resolve().parent;dest=root/'tool';(dest/'src').mkdir(parents=True,exist_ok=True)
src=root.parent/'simd-prefilter-20261015/tool'
for name in ['Cargo.toml','Cargo.lock']:(dest/name).write_bytes((src/name).read_bytes())
(dest/'src/prefix.rs').write_bytes((src/'src/prefix.rs').read_bytes())
(dest/'src/fast_sim_wide.rs').write_bytes((root.parent/'prefilter-20261015/tool/src/fast_sim_wide.rs').read_bytes())
(dest/'simd8wide.h').write_bytes((root.parent/'prefilter-20261015/simd8wide.h').read_bytes())
for name in ['zero8.c','build.rs']:(dest/name).write_bytes((root/name).read_bytes())
(dest/'src/main.rs').write_bytes((root/'main.rs').read_bytes())
