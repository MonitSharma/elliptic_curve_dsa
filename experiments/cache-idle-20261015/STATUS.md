# Idle-wire expression retention: terminal, rejected as an improvement

Both runs and fixed replays completed, exit 0. **No qualified score.** The
larger expression cache uses no additional qubits (diagnostic Q1235), but saves
only **3.0625 executed Toffolis per shot** in both 256-shot packets, worse than
the prior 4.015625 saving at that width. Preserve the earlier configuration.

The 32/200,000 configuration reproduces the original narrow candidate byte
for byte. At 128/1,000,000 there are 2,743 selected cache leases versus 2,738
previously; that increase does not translate into a net executed-gate benefit.
The simple branch-depth estimate incorrectly predicts an improvement. A more
accurate allocator would need a deterministic account of branch correlations,
without selecting or fitting hash-derived test packets.

Three native tests pass. Independent reconstruction checks every operation;
fixed event-aligned replay checks every quantum value, original classical bit,
phase and clean scratch. Both packet files match the previously frozen files.
Every comparison batch agrees. The inherited one independent failure and 189
structured failures remain. No official benchmark or submission was attempted.

[Receipt and exact sources](evidence/receipt.json) · [Evidence archive](evidence.tar.gz)
· [Portable external research source patch](research-crates.patch).
All 28 archived artifacts are verified locally. Protected B3 files match their
revision. Large streams remain in `/home/hclau/ecdsa_research/cache-idle-20261015/`;
launcher 3076107 is terminal.
