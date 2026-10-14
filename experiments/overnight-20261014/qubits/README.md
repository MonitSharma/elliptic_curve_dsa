# Qubit diagnosis, 14 October 2026

Status: **in progress; no qualified candidate or score**.

The existing `agents/qubits` compact reciprocal patch is preserved unchanged.
Server research lives exclusively in
`/home/hclau/ecdsa_research/overnight-20261014/qubits/`. Its `base` checkout is
clean public `c95b9325913abacca9c86bdebad10a20633cd04e`; `compact` has the
preserved existing patch. The three compact source SHA256 values match
`experiments/qubits/manifest.json` exactly.

`qubit-create-replay.py` generates a separate Rust diagnostic crate beside the
checkouts. It copies the protected evaluator's loader, secp256k1 parameters,
and Fiat–Shamir hashing function without editing them and imports the shared
clean-source simulator. It writes no official score or historical results.
The exact mode reconstructs all 9,024 compact-stream points and skips the
original measurement RNG by the number of `R`/`Hmr` operations times the prior
batch count. Its first replay is batch 18, containing shot 1170.

The paired mode reads the same exported point coordinates for either stream
and uses an independent fixed SHAKE seed. Random measurement choices occur at
different operation indices in the original and compact streams; phase masks
under paired mode are independent diagnostic checks, not an assertion of
identical internal measurement transcripts.

`qubit-packet-audit.py` independently reconstructs exact Euclidean values for
both point-addition denominators and checks the source's retained `EMAX=21`
valuation and map-region assumptions. This is a mathematical diagnostic, not
a full circuit simulation. The second denominator uses the reference output
coordinate, so a first-division circuit failure could cause subsequent actual
states to differ from that independent intended traversal.

All long jobs use `nohup`, a dedicated log, PID/exit files, source hashes,
one library thread, four build threads and a 128 GiB virtual-memory maximum.
Only one low-width stream job runs at a time. Complete logs and packet files
remain under `evidence/` on the server and the ignored local research output.
The clean-base stream job uses the public builder's existing exact-stream
serializer outside the official benchmark, without an identity-tail override;
the resulting stream and its hash are diagnostic evidence only.

## Commands

```bash
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
python3 qubit-create-replay.py base replay
CARGO_BUILD_JOBS=4 cargo +1.93.0 build --release --offline --manifest-path replay/Cargo.toml
nohup bash qubit-exact-batch18.sh > evidence/compact-exact-batch18.log 2>&1 < /dev/null &
echo $! > evidence/compact-exact-batch18.pid
# After its exit is collected and capacity is rechecked:
nohup bash qubit-build-base.sh > evidence/base-stream.log 2>&1 < /dev/null &
echo $! > evidence/base-stream.pid
python3 qubit-packet-audit.py evidence/compact-packet.tsv evidence/compact-packet-audit.json
replay/target/release/qubit_replay_diagnostic paired evidence/base-ops.bin evidence/compact-packet.tsv 18
```

The original failed stream and original server checkout are read-only inputs
to this research. Protected harness, simulator, curve reference, Cargo files,
toolchain and historical results in both submission checkouts remain intact.
