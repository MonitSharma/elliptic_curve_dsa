# Zero-MR coordinate slice — validated; rejection disabled

Backward quantum/classical liveness removes operations that cannot affect final
coordinate registers0/1. Unconditional overwrites kill earlier values; conditional
overwrites retain them. A live nested scope keeps its original Push snapshot and
matching Pop. Empty scopes are removed. Phase is not queried. A research-only
opcode range specializes depth-zero unconditional gates.

Full and statically simplified zero-MR evaluators match every protected quantum
and classical word on512 inputs for each of the public product source and old
four-stage candidate. All three sliced variants match both protected output
coordinates on those inputs. A512-assignment fixture exercises arbitrary quantum
and classical inputs, mutated nested guard snapshots, overwrite kills and dead
scopes; removing a live gate is detected by its negative control.

The latest run reduces the public value program from9,063,063 to7,944,811 ops,
and the candidate from9,271,954 to7,945,045. Specialized slice timings are2.97
and2.99ms per batch respectively, versus3.39 and3.57ms for static simplification
in the same runs. These are kernel timings under server load, not search costs.
Earlier attempts and an export compilation failure are preserved separately.

The full unsimplified public source still has23,093 live HMR classical
definitions in its output cone. Backward liveness therefore supplies no global
RNG-independence certificate. Fixed-zero simplification cannot supply that proof.
This evaluator remains disabled for nonce rejection until a separate proof
bound to the original stream and queried outputs is available.

Server library: `zero-mr-slice-20261016/libzero8_slice.so`, SHA256
84b73bcdee01bb537d0320f9985a682758d1076860455ad382a2ae175690ea82.
Its ABI matches the previous zero8_run API; exported compact programs use16-byte
little-endian rows and include output wire maps. `published.sha256` binds source,
library and programs; large server-only programs are not in the evidence archive.
