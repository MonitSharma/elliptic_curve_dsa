#!/usr/bin/env bash
# Run only inside the dedicated ECDSA workspace, never the chemistry repository.
set -euo pipefail
cd /home/hclau/ecdsa_research
mkdir -p logs
trap 'rc=$?; printf "%s\n" "$rc" > logs/bootstrap.exit' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
. /home/hclau/.cargo/env
rustup toolchain install 1.93.0 --profile minimal
if [[ ! -d upstream/.git ]]; then
  git clone https://github.com/Layr-Labs/ecdsafail-challenge.git upstream
fi
for item in \
  product:c5bb1ec876db859a3f9f8a9052c140a145df834e \
  toffoli:b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7 \
  qubits:c95b9325913abacca9c86bdebad10a20633cd04e; do
  track=${item%%:*}; revision=${item#*:}
  git -C upstream fetch origin "$revision"
  if [[ ! -e "$track" ]]; then
    git -C upstream worktree add --detach "../$track" "$revision"
  fi
  [[ $(git -C "$track" rev-parse HEAD) == "$revision" ]]
  [[ -z $(git -C "$track" status --porcelain) ]]
  ( cd "$track"; cargo +1.93.0 fetch --locked )
done
python3 -m venv .venv
.venv/bin/python -m pip install z3-solver==5.1.0.0
( cd product; /usr/bin/time -v cargo +1.93.0 build --release --locked --offline --bins )
( cd qubits; /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --bin build_circuit tests_midg_k24 -- --nocapture )
