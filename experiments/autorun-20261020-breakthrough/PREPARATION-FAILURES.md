Local preparation failures retained separately from circuit and gate results:

- V6 first one-line Python preparation had quoting syntax errors, made no
  source changes, and dependent generator/launcher rejected the missing run.py.
  Dedicated `prepare-compact-unitary-tail-v6.py` subsequently prepared the actual
  frozen source. Its native4 and full control passed; lowcaps failed fold guards.
- V8 helper first had an unterminated string in scope-document generation, so
  Python parsed nothing and created no candidate. An attempted one-line local
  PowerShell repair also failed parsing. The explicit patch corrected it before
  successful preparation, transfer and launch. Frozen V8 then passed native
  controls but exposed the separate fin1 selector mismatch, marked ineligible.

No statistical gate, nonce search or scored result ran in these failed local
preparations. The subsequent source freezes and original runtime failure logs
remain authoritative. Do not describe parsing failures as arithmetic failures.

Measurement terminology correction: Builder allocation emits no reset. `free`
emits R; `release_clean` emits none. Each omitted measured ripple/comparison carry
removes one HMR plus its release-R draw. The two-zero-HMR padding and every native
old/new RNG-count assertion always used the actual operation stream; early prose
calling R an allocation draw was inaccurate. No scored submission uses these new
comparator/targeted-ripple prototypes yet, and no gate verdict is being changed.

- Public-prefix27 helper initially failed Python parsing because outer/inner triple quotes collided. No directory, source freeze or server workload existed at that point. The delimiter was corrected and both generated scripts parsed before transfer/launch.
