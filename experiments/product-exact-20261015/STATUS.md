# Exact product savings, 15 October 2026

**Latest complete result: 33.64314651 ± 0.44141266 executed Toffolis saved per
shot at unchanged Q1234**, measured on the frozen compact eleven-stage source.
Normal native generation is byte-identical to the frozen external stream;
all 62 new native stage tests pass. Its full, predeclared fresh census includes
32,768 batches / 2,097,152 shots per source. The candidate has 4,109 failed
batches (**17.68093872 per packet**), versus the paired original's 4,126
(**17.75408936**). It meets the measured failure gate. Mean T is
761,189.7365369797 versus 761,223.3796834946. No nonce search, complete official
benchmark pass or scored product record is claimed by this experiment.
See `EXTENDED_FLAGS_FREEZE.json` and `compact11-census-summary.json`.

The later 25/32-stage measurements remain diagnostic while their native
source validation and separately declared census are pending. The coordinator
owns nonce qualification and unchanged official benchmarks.

## Historical four-stage evidence

**Exact rewrites meet the requested 12–15 T target in fresh census measurement:
14.55993557 ± 0.44253237 executed Toffolis saved per shot at unchanged Q1234.** No record,
full benchmark pass or submission is claimed. The frozen four-stage circuit
passes complete operation reconstruction and original-to-final measurement
mapping on 256 independent and 256 structured inputs: every quantum value,
original classical bit, phase and clean scratch agrees. Inherited arithmetic
failures remain unchanged.

**Fixed-packet measurement caveat (16 October):** the original replay assigns
random words while traversing each final circuit's measurement-event map. Added
cache measurements therefore shift the original events' random-word positions
between variants. Each parent/final equivalence check still aligns every
original event correctly within that pair, including phase. Its count saving
is a measurement on that particular coupled packet, not a universal exact mean
or an identical-randomness comparison with other variants. The original two
packets measured14.48828125T per shot. New variants will be ranked only after
`anchored-replay-20261016` fixes original measurement words by original event
ordinal and draws added cache measurements from a separate fixed stream.
The complete official benchmark and fresh large censuses remain authoritative.

**The first entirely fresh frozen-source census initially blocked nonce screening.**
On label `product-frozen-four-stage-20261015`, 4,096 batches / 262,144 shots,
the parent has 568 failed batches (**19.5527 per packet**) and the candidate
555 (**19.1052**). Both exceed the community cap of 18. The candidate's
diagnostic mean is 761,208.662674 T, saving **14.77850 ± 1.24678 T** in
paired measurement. This evidence is retained in full; no nonce was screened.

To reduce sampling error without selecting favorable packets, the sample
size was predeclared as **32,768 total batches / 2,097,152 shots per source**,
continuing the same label at batch 4,096 and including every initial batch.
The launcher never stops based on counts. See `DEEP_CENSUS_DECLARATION.json`.
That fixed larger census completed without optional stopping. The parent has
4,156 failed batches (**17.8831787109375 per packet**), and the candidate
4,144 (**17.83154296875**). The candidate is below the paired parent and the
cap of 18. Mean executed T is 761,223.2701225281 for the parent and
761,208.7101869583 for the candidate: **14.55993557 ± 0.44253237 T** paired
savings. See `frozen-deep-summary.json` and the complete included initial and
continuation batch files. No nonce search was performed by this experiment;
the coordinator owns subsequent qualification and unchanged benchmark runs.

## Frozen configurations and source port

The product pipeline is fixed before further census results:

1. Retained exact ANF support, atom cap 128, density lease ordering.
2. Ordinary immutable affine support, atom cap 128, density ordering.
3. Exact ANF support, atom cap 512, density ordering.
4. Retained exact ANF support, atom cap 512, density ordering.

Every stage uses product cap 1,000,000, ANF expansion cap 64 pairs, no new
quantum slots, exact cleanup and no packet-selected table or gate deletion.
The complete product stream is
`34a09e843bb182d0379fac82487ed26364711799c4126fbd7a4c1af7820ff5e6`.
`FREEZE.json` binds the configuration and source-native patch. The final
detached source tree is `candidate-final/`. **Normal build and generation
completed; the native output is byte-identical to the frozen external stream;
all 21 native point-addition stage tests passed.** The launcher exits zero.
`candidate-final.patch` changes exactly nine files, all under
`src/point_add/`; protected-file hashes match the source revision.

**Separate wide Toffoli objective:** the same predetermined four-stage chain
on our official source `5a7c3902` saves **23.03515625 T / shot at unchanged
Q1464**, again with complete state/phase equivalence in both 256-shot packets.
Independent inputs retain zero wrong values; the structured packet retains
the same 128 wrong values and four phase batches. `WIDE_FREEZE.json` binds
that separate circuit. Its source-native port completed, with byte-identical
stream and all 21 native tests passing. The frozen stream SHA256 is
`77b7fd4a760b0b639d36a7a28bac0c81af616aea205e1d7030f8bb29e97bbace`.
It has no qualified score here. The wide census uses a separate fixed
fresh label, `wide-frozen-four-stage-20261015`, 4,096 batches for the parent
and candidate. Both have 155 failed batches (**5.335693359375 per packet**).
Mean executed T is 753,764.2178993225 for the parent and 753,740.6572189331
for the candidate, a paired saving of **23.56068039 ± 0.79034210 T**.
This passes the failure-rate gate. The coordinator now owns nonce screening,
the unchanged benchmark and any queue entry, outside this experiment.

The source is the unmodified public record `4b2ec52fc55da796aa8f5ef851290297e8706424`.
Its rebuilt stream hashes to
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`, matching
the preserved original product-tip reproduction. The immutable stream was
also shared with the independent classical-prefilter work.

## Earlier single-pass evidence

The new structural cache allocator considers contiguous subsets of each
exact repeated-product group, so a busy wire lifetime does not invalidate
every shorter lease. Selection uses only immutable circuit expressions,
branch depth and operation positions. It does not profile benchmark packets.
It borrows only proved clean idle qubits and includes measured erasure with
the corresponding CZ phase repair.

All six variants and their baseline used label `product-exact-20261015`,
4,096 batches / 262,144 identical independent input shots:

| Atom cap / static order | Q | Paired saving T / shot ± SE | Failed batches / packet |
|---|---:|---:|---:|
| Original source | 1234 | — | 16.9365 |
| 32 / proxy | 1234 | 1.6718 ± 1.2400 | 17.3496 |
| 32 / density | 1234 | 2.8677 ± 1.2229 | 17.0742 |
| 128 / proxy | 1234 | 4.8947 ± 1.2438 | 17.2119 |
| 128 / density | 1234 | **5.4773 ± 1.2230** | 17.3496 |
| 512 / proxy | 1234 | 3.9606 ± 1.2628 | 17.3152 |
| 512 / density | 1234 | 4.0373 ± 1.2174 | 17.1086 |

Original mean: 761,222.2687072754 T. Best diagnostic mean:
761,216.7914009094 T. These are census diagnostics, not benchmark scores.
Additional cache measurements shift subsequent measurement randomness;
the independent replay therefore aligns every original measurement event.
That replay reconstructs **every emitted operation**, then confirms every
original quantum value, classical bit, phase and clean scratch on 256
independent and 256 structured shots. Both packets save exactly 1,413 T
total, or 5.51953125 T / shot. The inherited independent one wrong output,
and structured 189 wrong outputs and four phase batches, remain identical.

No nonce search was performed. The exact rewrites preserve semantics but
the census estimates are not a qualification or an all-input correctness
claim for the inherited approximate circuit.

The earlier split-cache configuration is now ported into a detached
source-native candidate, with frozen constants rather than environment-selected
cache settings. The patch is `candidate-split128.patch`; it changes only four
files under `src/point_add/`. Its normal source build and generation both
finish successfully. Its emitted stream is **byte-identical** to the external
diagnostic, SHA-256
`ba1454425342c617369e738608e23b4972f71b129c9d011e2f6b36deef5b3e16`.
This provides a reviewable source implementation; it is not a submission or
a complete benchmark pass.

## Negative results and continuing work

- Larger ordinary immutable-expression witness/simplification passes at
  caps 128, 512 and 2,048 emit the exact original product stream.
- Exact ANF expansion adds distributivity and square-free monomials, with
  conservative opaque fallbacks. Cap 128 removes one product operation;
  its paired census saves **0.500912 ± 0.000985 T / shot**, with all 4,096
  pass/fail outcomes identical. Complete identical-measurement replay saves
  0.5078125 T / shot in both 256-shot packets, preserving every value and
  phase. Other tested small caps leave
  the stream unchanged. The wider source has small additional linear
  rewrites, separately reported to the coordinator.
- Exact interval remapping keeps Q1234, so it does not lower the product.
- Exact commuting-Toffoli guard-parity fusion merges 8,796 operations into
  2,526 windows but saves **zero T** across all 4,096 paired batches. Counts
  and all batch pass/fail outcomes are identical. Those branches partition
  the same work rather than duplicate executed work. The wide source has
  no eligible sites.
- Semantic restoration of final cache controls recovers zero additional
  cleanup proofs on the tip.
- Exact borrowing from a clean wire used only under disjoint classical
  guards passes a dedicated exhaustive small regression. Initial cap-32
  product runs and cap-128 runs select zero additional conditional donors.
- ANF-backed width-free cache at cap 512 saves **6.06924 ± 1.24419 T** in
  the paired 262,144-shot census. Event-aligned confirmation and larger
  conservative proof-cap experiments continue; no record is claimed.
- Conditional and complemented live-wire witnesses find no product sites
  at caps 128 and 512. A wide-source site is separately reported to the
  coordinator; it is not a product result.
- The coordinator's exact lazy single-AND pass selects three product sites,
  then zero sites on each of three additional passes. Identical-measurement
  replay preserves all values and phase but saves exactly zero T in both
  256-shot packets.
- Moving unconditional resets/measurements earlier without crossing any
  target or result-bit dependency moves 353,427 events by a total 53,885,540
  positions. Complete event-permuted replay preserves all values, original
  classical bits and phase in both 256-shot packets. Compaction remains
  Q1234 and cache opportunities remain unchanged. Its census is diagnostic.

The native regression coverage now has 21 passing tests, including
all-input conditional borrowing, busy-lifetime splitting, guard-parity
fusion, phase-reader blocking and a deliberately removed phase correction.

All work is isolated under
`/home/hclau/ecdsa_research/product-exact-20261015/`. Dedicated launchers,
PID/exit files, preflights, source, stream hashes, generation logs and census
files remain there. Only research files have been written locally; the
public source and all protected harness files are unchanged. No commits,
pushes or submissions were made.

## Frozen compact continuations and independent qualification

The compact eleven-stage source passes 62 native tests and normal generation
matches its external stream byte for byte (SHA256
`2a7429e1f5655820c461279b4d2479449450ce819ddbc784c5de481d31691e97`).
It keeps Q1234 and 46,508 classical slots. Its anchored 512-shot diagnostic
saving is 33.47265625 T. A newly declared 32,768-batch paired fresh census
uses every batch under `product-compact11-frozen-20261016`; qualification is
pending and no partial rates will be used for selection.

The fixed 25-stage continuation completes both full anchored reconstructions
with 58.47265625 T diagnostic saving, Q1234 and 47,921 classical slots.
Its stream hash is
`180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64`.
The native port reuses five pure helper configurations across 25 calls;
`PRODUCT25_FREEZE.json` records every stage and its source patch. Generation,
full byte comparison and native tests precede its separate predeclared fresh
32,768-batch paired census. It never replaces or edits the eleven-stage source.

A further four seven-stage cycles, ending at stage 53, were declared before
measuring them. The fixed checkpoints are 32, 39, 46 and 53. This separate
experiment uses the same anchored original-event RNG protocol, compact donor
flags, a single analysis thread and a 40-GiB virtual-memory limit. It is
component research until a final frozen source, native proof and fresh gate.

The fifteen-stage wide source is separately frozen at Q1468 and 41.94921875 T
anchored saving. It has four extra quantum slots. Native full-stream identity,
its stage tests and a fixed 4,096-batch paired fresh census remain required.
The original queued wide four-stage result is unchanged.

A source-only feasibility probe restores every inherited census deletion row
as a whole structural family, after all original neighborhood anchors have
validated. All reduction rows and upstream tables remain unchanged. The fixed
choice is recorded in `CATEGORY_RESTORE_DECLARATION.json`; this initially
measures construction and cost only, without a census or nonce search.
