# Matched unbound square diagnostics

These experiments use the documented `Y42_UNBOUND=true`, `Y42_ALLOC=false`
research mode. Each payload returns to its saved allocator state with generic
set/counter assertions; no recorded allocator signature is copied onto a
changed tree. Only `src/point_add/` is changed and all protected files remain
untouched. This mode is diagnostic, not a qualified original candidate.

The baseline's raw production emission succeeded, while its later complete
builder pipeline failed at `linear_restore.rs`, exit 101: expected operation
table length 11,459,358, observed 11,274,530. `Y42_UNBOUND` omits the documented
Y42-bound edits, but does not omit this later bound pass. We preserve this
failure and do not claim a complete generic pipeline or original-baseline byte
identity. The raw vector includes the actual square and subsequent multiply.

The baseline native consumer completed exit 0 on the same first 64 structured
points and measurement domain as the earlier coupled-consumer diagnostic.
Coordinates fail on 18/18 literal-zero slopes and 32/32 `P=-2A` cases. Physical
p zero slopes have correct coordinates. All scratch qubits are clean and the
classical coordinate ABI is unchanged. Phase failures are separate:

| Endpoint | Literal 0 (18 shots) | Physical p (14 shots) | P=-2A (32 shots) |
|---|---:|---:|---:|
| Coordinate-y subtraction | 0 | 0 | 0 |
| Division | 8 | 6 | 0 |
| Square | 9 | 6 | 0 |
| Multiply and final coordinate-y subtraction | 9 | 6 | 15 |

Thus coordinate success of a p-represented zero is not a phase-qualified pass.
The square residue repair experiment cannot by itself repair the inherited
division phase issue or singular multiply issue.

An attempted full-width run reused the previous baseline `build_circuit`
artifact from a shared Cargo target directory. Its binary hash was identical
to the baseline (`0f643ccab2450e30598633f9f3d86139c2f4a8a8d03b24a1d848041c207f2d38`)
and its runtime snapshot path was `unbound-base` rather than `unbound-full-cross`.
The native consumer stopped at a missing full-cross stream, exit 1, before any
simulation. This run is **invalid_cached_binary** and is excluded from all
full-width arithmetic evidence. Its source, logs, receipts and failure remain
preserved. The overwritten baseline raw file was rechecked against its original
pre-replay SHA256 and is unchanged (`cd8e47b231cee72de1eb984b546bfefb99333118bcbec6d447d913778eb169e5`).

The corrected full-width run uses a fresh dedicated Cargo target directory.
Its builder binary is distinct
(`b34a3eaa64898f89672e8d795380110d1658129383e98a82d26267ad23733d3f`)
and runtime snapshot path is correctly `unbound-full-cross-v2`. Raw emission
contains 11,272,753 operations, versus 11,269,315 for the matched baseline.
The native coupled-consumer check completed exit 0 in a separate dedicated
target. The [matched consumer receipt](unbound-matched-consumer-receipt.json)
asserts distinct source-bound builder binaries, correct runtime paths and the
**same** native helper binary for both streams. Both later complete builder
pipelines still fail their bound `linear_restore` length check, exit 101.

| Final family | Baseline x/y failures | Full-width x/y failures | Baseline phase shots | Full-width phase shots |
|---|---:|---:|---:|---:|
| Literal 0, 18 shots | 18 / 0 | 18 / 0 | 9 | 14 |
| Physical p, 14 shots | 0 / 0 | 0 / 0 | 6 | 6 |
| P=-2A, 32 shots | 0 / 32 | 0 / 32 | 15 | 20 |

All quantum scratch remains clean and classical coordinate inputs are unchanged
in both. Full-width R0 sign extensions remain uniform and odd. Its 18 literal
zero residue errors now share expected-minus-actual delta
`0xffc00001000003d400000b73fffff86100000b7600000b6bffffe54c000e9c14`.
Thus retaining the full assembly path does **not** repair the arithmetic.
The shared random domain does not align later measurement positions after
changing carry paths, so the phase counts do not establish a comparative error
rate. No independent repair follow-up was launched because this repair failed.

An [independent unsigned integer model](zero-karatsuba-model.py) uses actual
split thresholds, wraps each leaf's `x²-2` into its finite word, subtracts the
physical child words, and applies the source-top masking assumption and E=18
assembly cut. This reconstruction reproduces the baseline's constant residue
error exactly. The corresponding full-assembly reconstruction differs from
the observed full-width error by exactly `-2^246 mod p`. The model does not
simulate dirty borrowed wires or phase cleanup, and is not an all-input proof;
that remaining bit motivates directly observing the actual producer/loan
interfaces before changing further switches. Row-zero copy is still enabled.

All future changed-checkout builder/test runs use dedicated target directories.
The dependency registry cache may be shared. Source hashes, runtime diagnostic
path and native binary hash must agree before interpreting any result.
