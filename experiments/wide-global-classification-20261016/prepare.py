from pathlib import Path
import hashlib,shutil
root=Path(__file__).resolve().parent;base=root.parent/'product-exact-20261015/loan-normal-forms-tool';tool=root/'tool';(tool/'src').mkdir(parents=True,exist_ok=False)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(base/name,tool/name)
kernel=(root.parent/'current-value-attribution-20261016/donor-support-original.rs').read_bytes();assert hashlib.sha256(kernel).hexdigest()=='c262bba163fe91a6f2bd72e21fd387de84b426838b1bba113f017b18ed9cfa71';source=kernel.decode();needle='let rewrite = Self::ccx_rewrite(&condition, &a, &b, op);';assert source.count(needle)==1
hook='\n                observe_global(&condition, &a, &b, op, &rewrite, self.condition_stack.len());'
instrumented=source.replace(needle,needle+hook);assert instrumented.replace(hook,'')==source
(tool/'src/support.rs').write_text(instrumented+'\n'+(root/'observer.rs').read_text());(root/'immutable-kernel.rs').write_bytes(kernel)
main=(base/'src/main.rs').read_text();start=main.index('fn main(){');main=main[:start]+'''fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);let ops=load(&args[1]);support::run_global_classification(&ops);}\n''';(tool/'src/main.rs').write_text(main)
