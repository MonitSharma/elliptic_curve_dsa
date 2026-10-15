from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'masked-witness-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
mask=(tool/'src/masks.rs').read_text().replace('*mut u64)->i32','*mut u64,usize)->i32')
mask=mask.replace('mask-evaluator-20261016/libmask8.so','mask-width-20261016/libmask_width.so').replace('641f8c1b6578c9878244650bd05cbbbd1fd452e9199c504bc76832cf72fd81e1','120dc358f57329e48cdd7bdf26e86ad47b0d84b07d4338227a086ed0c07562f2').replace('b"mask8_eval\\0"','b"mask8_eval_width\\0"')
needle='p.roots.as_ptr(),512,out.as_mut_ptr())'
assert mask.count(needle)==1;mask=mask.replace(needle,'p.roots.as_ptr(),512,out.as_mut_ptr(),points.len().div_ceil(64).max(1).next_power_of_two())')
(tool/'src/masks.rs').write_text(mask)
body=(tool/'src/packed_body.rs').read_text();assert 'threads<=16' in body;body=body.replace('threads<=16','threads<=32');(tool/'src/packed_body.rs').write_text(body)
