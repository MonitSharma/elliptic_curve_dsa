from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'product-fused-filter-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
shutil.copyfile(root/'early.rs',tool/'src/early.rs')
source=(tool/'src/packed_body.rs').read_text();source='include!("early.rs");\n'+source
needle='let program=zero_program();mask_program();'
assert source.count(needle)==1;source=source.replace(needle,'let program=zero_program();mask_program();let full=Compact::compile(&ops[..n-TAIL]);if std::env::var_os("EARLY_FULLSTATE_SHADOW").is_some(){validate_early(&ops,&full,&hash,tail,&regs,nq,nb,&curve);}')
needle='let packet=&pending[index].0;let mut actual=ops[..n-TAIL].to_vec();actual.extend(nonce_tail(tail,packet.nonce));let result=run_tests(&actual,&regs,nq as u64,nb as u64,fiat_shamir_seed(&actual),NUM_TESTS);fallback_secs+=t.elapsed().as_secs_f64();writeln!(out.lock().unwrap(),"{}",serde_json::json!({"nonce":packet.nonce,"provisional_wrong_value":false,"candidate_full_fallback_pass":result.ok,"authoritative_rejection":false,"proof_accepted":false,"witnesses_tried":packet.attempts,"protected_shots":result.n_shots})).unwrap();remove[index]=true;'
replacement='let packet=&mut pending[index].0;let(kind,early_shots)=exact_early(&full,packet,&regs,nq,nb,&curve);let mut pass=false;let mut protected_shots=0;if kind=="pass"{let mut actual=ops[..n-TAIL].to_vec();actual.extend(nonce_tail(tail,packet.nonce));let result=run_tests(&actual,&regs,nq as u64,nb as u64,fiat_shamir_seed(&actual),NUM_TESTS);pass=result.ok;protected_shots=result.n_shots;}fallback_secs+=t.elapsed().as_secs_f64();writeln!(out.lock().unwrap(),"{}",serde_json::json!({"nonce":packet.nonce,"provisional_wrong_value":false,"candidate_full_fallback_pass":pass,"authoritative_rejection":false,"proof_accepted":false,"witnesses_tried":packet.attempts,"protected_shots":protected_shots,"exact_early_kind":kind,"exact_early_shots":early_shots})).unwrap();remove[index]=true;'
assert source.count(needle)==1;source=source.replace(needle,replacement);(tool/'src/packed_body.rs').write_text(source)
