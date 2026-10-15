# Prefilter macro source mapping and universal value certificates

Original public source 4b is unchanged. Two gate-inert source observers emit
the same entire raw builder stream SHA256
`ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69`, bound
to final public stream
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
Protected harness, simulator and Cargo files are unchanged.

The first global symbolic precision loss at final operation 688826 is inside
forward tick-3's Y21 top1 cleanup, specifically its false `nbx & bit0` branch.
The complete clause spans both bitx branches and an intervening unconditional
HMR, which explains why a closed-Push-only proof scan misses its composition.
The full source argument, exact offsets, dirty-state semantics and inherited
raw/final edit diff are in `SOURCE-ARGUMENT.md` and the JSON evidence.

Delivered exact final-stream intervals to the independent prefilter prover:

| Family | Candidate intervals | Universally proved reset projection |
|---|---:|---:|
| Complete Y21 top1 clauses | 250 | 250 |
| Source-derived comparator candidates | 547 | 547 |

These proofs quantify over arbitrary quantum entry values, classical entry
bits and measurement outcomes, including dirty auxiliary states. They retain
every original R/HMR draw, conditional classical write and Push snapshot.
The prefilter agent also validated its broader closed-scope projection on
every quantum wire and classical bit on 5,132 protected shots, including all
541 preserved failures, structured/arbitrary cases, two measurement seeds,
and fully dirty auxiliary controls. Phase deliberately remains outside these
value-only certificates.

All TSV ends are exclusive. `comparator-proof-spans.tsv` is the initial
114-span conservative subset; `comparator-proof-spans-v2.tsv` contains all
547 candidates. `complete-top1-proof-spans.tsv` contains the 250 complete
clauses. The independent exact final-span proof is the acceptance gate;
source-anchor labels and finite replays do not replace it.

The first 1009-operation false branch has 43 identity quantum outputs and 37
conditional resets under the two captured outer bits, without assuming any
scratch input is zero. The source-only raw branch has 1001 operations because
an inherited pass deletes its top scratch AND and replaces phase terms.
This inherited difference is preserved and handled by proof of actual final
operations rather than a source-model assumption.

The global RNG-independence proof remains the prefilter agent's work in
progress. These local proofs do not by themselves authorize direct nonce
rejection. No circuit source, scored packet, nonce, public result, commit or
submission was changed by this work.
