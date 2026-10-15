from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'prefilter-20261015';tool=root/'tool';(tool/'src').mkdir(parents=True,exist_ok=True)
for n in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/n,tool/n)
for n in ['official.rs','fast_curve_c.rs','fast_sim_wide.rs','rail_advisory.rs','simd_screen_ffi_wide.rs']:
 shutil.copyfile(old/'tool/src'/n,tool/'src'/n)
source=(old/'tool/src/bin/bucket_fast_wide_screen.rs').read_text().replace('../','').replace('include!("bucket_fast_screen_body.rs");','include!("baseline_body.rs");\ninclude!("packed_body.rs");')
(tool/'src/main.rs').write_text(source)
(tool/'src/baseline_body.rs').write_text((old/'tool/src/bucket_fast_screen_body.rs').read_text().replace('fn main(){','fn baseline_main(){',1))
source=(old/'tool/src/rail_fast_ffi.rs').read_text().replace('fn rail_suspect_many(model:&RailAdvisory,points:&[PointTriple])->bool','fn rail_flags(model:&RailAdvisory,points:&[PointTriple])->Vec<u8>').replace('flags.iter().any(|x|*x!=0)','flags')
source+='\nfn rail_suspect_many(model:&RailAdvisory,points:&[PointTriple])->bool{rail_flags(model,points).iter().any(|x|*x!=0)}\n'
(tool/'src/rail_fast_ffi.rs').write_text(source)
shutil.copyfile(root/'packed_body.rs',tool/'src/packed_body.rs')
