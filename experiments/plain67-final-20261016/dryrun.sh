#!/usr/bin/env bash
# Dry run of the PLAIN67 finalization with a fake audit selecting nonce 12345 (not a pass).
# Exercises prepare/native tests/build/generate/native receipt/tail invariance; skips the benchmark.
set -euo pipefail
r=/home/hclau/ecdsa_research/plain67-final-20261016
d=$r/dryrun
test ! -e "$d"
mkdir "$d"; cp "$r/finalize.py" "$d/"
echo $$ > "$d/dryrun.pid"
trap 's=$?; echo "$s" > "$d/dryrun.exit"' EXIT
echo '{"status":"LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS","lowest_full_protected_pass":12345,"dry_run":true}' > "$d/ROOT_TERMINAL_AUDIT.json"
ulimit -v 50331648
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export RUSTFLAGS='-C linker=/usr/bin/gcc'
unset RUSTUP_TOOLCHAIN CARGO_TARGET_DIR
python3 "$d/finalize.py" prepare > "$d/prepare.log" 2>&1
cd "$d/candidate"
cargo test --release --locked --offline --bin build_circuit frozen_cache_product67 -- --test-threads=1 > "$d/native-tests.log" 2>&1
grep -q '4 passed; 0 failed' "$d/native-tests.log"
cargo build --release --locked --offline --bin build_circuit > "$d/build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "$d/generate.log" 2>&1
python3 "$d/finalize.py" native > "$d/native-verification.log" 2>&1
cp ops.bin "$d/native-selected.ops.bin"
python3 "$d/finalize.py" tailcheck > "$d/tailcheck.log" 2>&1
python3 - "$d" <<'EOF'
import json, sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
exec(Path("/home/hclau/ecdsa_research/plain67-final-20261016/audit-terminal.py").read_text().split("if __name__")[0])
print(json.dumps(audit_lane(Path("/home/hclau/ecdsa_research/plain67-operational-20261016/control/rows.jsonl"), 0, 4096)["dispositions"]))
EOF
