from pathlib import Path
import hashlib,shutil
root=Path(__file__).resolve().parent;base=root.parent/'product-exact-20261015/loan-normal-forms-tool';tool=root/'tool';(tool/'src').mkdir(parents=True,exist_ok=False)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(base/name,tool/name)
kernel=(root.parent/'current-value-attribution-20261016/donor-support-original.rs').read_bytes();assert hashlib.sha256(kernel).hexdigest()=='c262bba163fe91a6f2bd72e21fd387de84b426838b1bba113f017b18ed9cfa71'
(tool/'src/support.rs').write_bytes(kernel+b'\n'+(root/'cofactor.rs').read_bytes())
main=(base/'src/main.rs').read_text();start=main.index('fn main(){');main=main[:start]+'''fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);let ops=load(&args[1]);println!("{}",support::run_cofactor_census(&ops));}\n''';(tool/'src/main.rs').write_text(main)
