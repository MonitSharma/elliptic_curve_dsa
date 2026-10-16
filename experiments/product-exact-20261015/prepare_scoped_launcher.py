from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'run-guard-cache-weighted.sh').read_text().replace('guard-cache-weighted-20261016','scoped-cache-20261016').replace('prepare_guard_weighted.py','prepare_scoped_cache.py').replace('guard-cache-weighted-tool','scoped-cache-tool').replace('target-guard-cache-weighted','target-scoped-cache').replace('target-anchored-replay','target-scoped-replay').replace('Existing exact retained ANF cache rewrite, compact flags, no extra qubits.','Scoped exact cache leases start at first use and end in lexicalLCA after last nested scope; next-write fence on cleanup controls, untouched zero donors. Global unconditional privateflag initialization plus conditional end resets preserve dirtyABI and disjoint donor reuse. No extra qubits.')
needle='for family in product wide; do'
assert s.count(needle)==1
s=s.replace(needle,'CARGO_TARGET_DIR="$root/target-scoped-replay" cargo build --manifest-path scoped-replay/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/replay-build.log" 2>&1\n'+needle)
(r/'run-scoped-cache.sh').write_text(s,newline='\n')
