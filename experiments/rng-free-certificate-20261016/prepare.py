from pathlib import Path
root=Path(__file__).resolve().parent;src=root.parent/'simd-prefilter-20261015/tool';dest=root/'tool'
(dest/'src').mkdir(parents=True,exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:(dest/name).write_bytes((src/name).read_bytes())
for name in ['prefix.rs','fast_sim.rs']:(dest/'src'/name).write_bytes((src/'src'/name).read_bytes())
for name in ['main.rs','tri.rs']:(dest/'src'/name).write_bytes((root/name).read_bytes())
