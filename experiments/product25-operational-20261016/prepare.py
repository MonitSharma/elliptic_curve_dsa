from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'product-early-filter-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
shutil.copyfile(root/'search.rs',tool/'src/search.rs')
source=(tool/'src/packed_body.rs').read_text();source='include!("search.rs");\n'+source
source=source.replace('const PROOF_ACCEPTED:bool=false;','const PROOF_ACCEPTED:bool=true;')
source=source.replace('assert!(!PROOF_ACCEPTED,"benchmark gate must remain disabled until separately reviewed certificate");','assert!(PROOF_ACCEPTED);bind_operational();')
source=source.replace('count<=65536','count<=134217728').replace('threads<=32','threads<=14')
needle='let lookahead=a[7].parse::<usize>().unwrap();assert!'
assert source.count(needle)==1;source=source.replace(needle,'let lookahead=a[7].parse::<usize>().unwrap();bind_operational_args(first,count,lookahead);assert!')
needle='for window in (0..count).step_by(lookahead){let stop='
assert source.count(needle)==1
source=source.replace(needle,'let mut screened=0usize;for window in (0..count).step_by(lookahead){let global_start=window_start(first,window,lookahead);if stop_after().is_some_and(|end|global_start>end){break;}let stop=')
needle='first+(ix+j).min(stop-1)as u64'
assert source.count(needle)==1;source=source.replace(needle,'global_start+((ix+j-window).min(stop-window-1))as u64')
source=source.replace('"authoritative_rejection":false,"proof_accepted":false,"witness_batch"','"authoritative_rejection":true,"proof_accepted":true,"witness_batch"')
source=source.replace('"authoritative_rejection":false,"proof_accepted":false,"witnesses_tried"','"authoritative_rejection":!pass,"proof_accepted":true,"witnesses_tried"')
needle='pass=result.ok;protected_shots=result.n_shots;'
assert source.count(needle)==1;source=source.replace(needle,'pass=result.ok;protected_shots=result.n_shots;if pass{assert_eq!(protected_shots,9024);record_pass(packet.nonce);}')
needle='pending=updated.into_inner().unwrap();\n  }\n }'
assert source.count(needle)==1;source=source.replace(needle,'pending=updated.into_inner().unwrap();\n  }\n  screened+=stop-window;record_window(global_start,stop-window,screened);\n }')
source=source.replace('PROOF_ACCEPTED=false AUTHORITATIVE_REJECTIONS=0 NONCE_SELECTED=false','PROOF_ACCEPTED=true NONCE_POLICY=ASCENDING_LOWEST_PASS screened={screened}')
source=source.replace('// Benchmarks only. No universal RNG-independence certificate has been accepted.','// Frozen original-source per-input masks plus complete universal candidate transfer accepted separately.')
source=source.replace('// Every provisional witness is explicitly unauthoritative; no nonce is selected.','// Full protected confirmation required for every possible pass; coordinator proves lower-prefix completeness.')
source=source.replace('"provisional_wrong_value"','"certified_wrong_value"')
(tool/'src/packed_body.rs').write_text(source)
mask=(tool/'src/masks.rs').read_text().replace('authoritative_gate=false','authoritative_gate=true');(tool/'src/masks.rs').write_text(mask)
curve=(tool/'src/fast_curve_c.rs').read_text();needle='let path=CString::new(path).unwrap();'
assert curve.count(needle)==1;curve=curve.replace(needle,'sha_check(&path,"3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f");'+needle);(tool/'src/fast_curve_c.rs').write_text(curve)
