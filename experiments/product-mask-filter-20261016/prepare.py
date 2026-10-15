from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'masked-width-witness-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
body=(tool/'src/packed_body.rs').read_text()
body=body.replace('"2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e"','"180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64"')
needle='let n=ops.len();let tail='
assert body.count(needle)==1
body=body.replace(needle,'let n=ops.len();assert_eq!(n,14_142_629);bind_transfer();let tail=')
needle='let witness=packet.next_witness(&curve,&model);'
assert body.count(needle)==2
body=body.replace(needle,'let witness=if std::env::var_os("FORCE_FULL_FALLBACK").is_some(){None}else{packet.next_witness(&curve,&model)};')
needle='let curve=FastCurveC::new(20);'
assert body.count(needle)==1
body=body.replace(needle,'if std::env::var_os("CANDIDATE_SEED_SHADOW").is_some(){check_candidate_seeds(&ops,&hash,tail);}\n '+needle)
body=body.replace('original_full_fallback_pass','candidate_full_fallback_pass')
body='include!("transfer.rs");\n'+body
(tool/'src/packed_body.rs').write_text(body);shutil.copyfile(root/'transfer.rs',tool/'src/transfer.rs')
