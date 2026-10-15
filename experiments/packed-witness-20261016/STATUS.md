# Packed suspect-input benchmark — universal proof still required

This fixed-range benchmark packs one advisory-suspect input from each of up to512
different nonces into an eight-word value simulation. When a suspect passes,
it advances to another suspect. No remaining suspect triggers the original full
simulator. It uses the original Fiat input transcript and a separately validated
fixed-zero-MR coordinate program.

**Rejection is disabled.** A universal source-bound theorem that all queried
coordinates are independent of measurement randomness has not been accepted.
Every reported wrong value is explicitly provisional; authoritative rejects are
zero, no nonce is selected, and the benchmark is capped at4096 fixed nonces.

Protected fixed-zero coordinate comparisons pass for128 nonces and the partial
17..27 range. For fixed nonces1..1024,1036 suspect inputs suffice:7.351762 seconds
at2workers and1.236710 at16. Preparation dominates (7.131087/1.016466seconds);
packed value work takes0.093330/0.111062seconds. These are disabled benchmark
timings, not an operational exact search or a resource record. The first syntax
failure is preserved. The follow-up packed-stream experiment avoids reading all
9024 scalar-pair inputs before finding the first suspect.
