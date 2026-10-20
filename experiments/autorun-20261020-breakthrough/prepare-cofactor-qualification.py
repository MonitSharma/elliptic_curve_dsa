from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-semantic-guards-audit-v2-20261020';r=ex/'breakthrough-value-cofactor-qualification-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
for n in ['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
core=(old/'audit.rs').read_bytes();extra=b'''
#[cfg(test)]mod above_bound_cofactor_tests{use super::*;
 fn masked(enable:bool)->(u32,u32){let mut e=Expr::default();e.restricting=!enable;let mut g=1;for _ in 0..6{let a=e.atom();g=e.and(g,a);}let mut old=1;for _ in 0..6{let a=e.atom();old=e.and(old,a);}assert_eq!(e.semantic(g).atoms.len(),6);assert_eq!(e.semantic(old).atoms.len(),6);let random=e.atom();let value=e.ite(g,random,old);let got=e.and(g,value);let expected=e.and(g,random);(got,expected)}
 #[test]fn masked_alias_above_six_atom_bound_requires_and_exercises_cofactor_rule(){let disabled=masked(false);assert_ne!(disabled.0,disabled.1,"negativecontrol must fail to canonicalize when exact cofactoring disabled");let enabled=masked(true);assert_eq!(enabled.0,enabled.1);}
}
''';(t/'audit.rs').write_bytes(core+extra);(r/'qualification-tests.rs').write_bytes(extra);f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(source_files={n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs']},native_controls=26,original_production_core_sha256=sha(core),scope='Append cfg(test) ONLY; all production cofactor/semantic code byte prefix unchanged. New exact six-plus-six-plusrandom support regression includes rule-disabled negativecontrol; unlike8atom conjunctions, each support stays exactly6 before large union, so this genuinely exceeds tablecap. Existing25 tests retained. No main audit/input/nonce/gate run.');(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-value-cofactor-qualification-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export CARGO_TARGET_DIR=BASE/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path local-tool/Cargo.toml --bin value_semantic_guards_v2_audit -- --nocapture > tests.log 2>&1
grep -q 'test result: ok. 26 passed; 0 failed;' tests.log
'''.replace('BASE',base)).encode());print(r.name)
