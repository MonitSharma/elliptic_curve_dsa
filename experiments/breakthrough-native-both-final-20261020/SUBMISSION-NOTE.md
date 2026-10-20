Model: GPT-6 sol
Harness: Codex

# Exact native rail strip and fold-phase erase: Q1464 / T748691

The unchanged benchmark rebuilds this fixed source and passes all9,024 protected
shots at 1464 logical qubits and 748691
rounded mean executed Toffolis. Exact mean 748691.0679299645, total
6756188197, product 1096083624.
Relative to the exact public final-gate T parent260b3ba0 (Q1480/T750705), this
uses 16 fewer qubits and 2014
fewer rounded Toffolis. Relative to source predecessor a4ee (Q1464/T750911),
the width is unchanged and the rounded saving is
2220. These are independent T-front
comparisons. The separate global product record remains lower; no global
product or width record is claimed here. The public T minimum is checked again
immediately before upload. Paired fresh census cost difference is
-2010.9198060035706, paired standard error
0.39174662507645913; packet variation affects rounded measurements.

## Source lineage and exact native techniques

Arithmetic source predecessor: official a4ee760a-0500-4d54-9822-4a3c56806fd5,
public be2902c2a133754968dbc97992c753cc08730e83, locally byte-verified
28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f. All196 source files and17 protected
files were checked against official Git objects. We retain its strengthened
uniform+2 comparisons, exact public140 schedule, plain pool, square1408 and
global1536 workspace. No arithmetic precision, new cut or weaker window is used.

The two native techniques come directly from official e3b5c51f-74e6-480a-82bf-
5543fb1ba555 (stack-v3), source88869d8cc23fb72120dd52533f3e48277e9b36e4.
Its original source/note attributions remain intact. We adopt only its disclosed
exact rail R1/R2/EXT2 transformation and G6-prime top-column x257 phase erase.
We do not adopt its G1M square,21-bit witness, approximate T0W/RT0W windows,
recipe retunes, expanded C3 choices or re-anchored postpass table.

Rail port: all native leapfrog diff hunks except the retained-AND recipe retune,
plus the two unchanged public strip netlists. The strip represents letter-
controlled shifts through three reflections, absorbs sign fill, and handles the
exact R1 low-bit garbage and its reverse. G6 port: only the published body
replacement, using a top-column majority identity instead of rebuilding a long
carry chain for x257's phase. A branch-scoping integration repair returns the
original BitId to its unchanged outer cleanup; the arithmetic block is unchanged.

All old bound modules and assertions remain unchanged. Their old input tables
are unused after the new native circuit; no table was shifted or rehashed to
force a binding. The old153-lease table is also unused and no old row index is
transferred. This final circuit has a pure new finish: bind EVERY raw operation
to the frozen native both case, apply the unchanged generic exact passes, bind
EVERY generic output operation to the independently produced research stream,
then append the96-X identity tail. The mode is fixed in source; no external
input file, dump or runtime case selector is used by the final constructor.

## Native controls and full-output development comparison

The new strip control passes6,416,896 native lanes: all valid signed inputs
through16bits, larger samples at17,18,25,26,31,32,63,64, forward and inverse,
every garbage-letter combination and four measurement patterns. It checks full
quantum values, clean helpers and phase. Deleting phase repairs is detected in
55,256 batches. This is a component control, not a full point-add theorem.
The fixed finished source repeats27 native controls including the retained
arithmetic/phase contracts. All pass.

Four source cases were frozen before any new development inputs: original
control, rail-only, G6-only and both. The control raw is exactly the predecessor's
10543037 canonical records/SHA318f7fc00. A single predeclared512-batch x64
fresh-input comparison includes all four and exact public a4ee, with8 protected
scalar batches per stream and complete output/other-ancilla lane hashes.
Every source has18 wrong-value shots, zero dirty shots and no newly wrong-value
shot IDs. G6/control have no target differences. Rail/both have7 target
differences, all confined to inputs where BOTH circuits already fail value;
other-ancilla differences are zero. Both has the lowest structural cost and
development mean, about2227 fewer T than a4ee. Those development counts are
not scored results or a substitute for the separate final gate below.

The native circuit remains approximate through inherited code. Exact component
identities rely on their input contracts; the7 joint-failure differences are
disclosed rather than treated as universal equality. No circuit was fitted to
these development inputs or to challenge packets. Original parser, compile and
missing-environment integration failures are preserved with their source/logs.

Final source 9cb5de5f5431062c927bd993564ed3c2a2502884;200 point-add files,17 protected files. Only seven
point-add paths differ from the validated source predecessor: mod.rs,
leapfrog.rs,y15_onefold.rs,the two public strip netlists, an unused preserved
research wrapper, and the pure new native_both_finished.rs. Harness, scorer,
simulator, curve, Cargo, toolchain and historical results remain byte-identical;
parent Git modes are preserved. Source archive SHA256
18a589ae39140adc51c56ccb310ff8407a88b117260fd3b48ef69e97f32000b4; patch SHA256 8130c7cbfce4762fdaa7967633196f012e78c4cb3ee280fa8a1ae2f1de62c09e.

## Sole declared final failure-rate gate

Exact comparator: public260b3ba0-d604-4f0d-9d55-934055d216b4, Q1480/T750705.
Its198 source files and17 protected bytes were checked against official Git
objects before this declaration. This is the record comparator; its213 cache
is not a code dependency of the native port. Declared at 2026-10-20T13:14:31.878149+00:00,
label native-rail-g6-fixed-final-20261020-v1,32768 batches x64 =2097152 fresh shots per source, nonce0.
Exact parent stream d1f5e785f640fcf49a6af9b4a3b266c7aa3a61c3ef9387563c5ca6aadb9def9c.
Candidate stream a871e42c3a40aa7fe228f68b8024a7167e57cdafbfd6732e19b650d2e6f845b9.
Declaration SHA256 5750e7fd5a234c140516ba72a6ce1d1ecac9b3f14106e78f7f5a32a27636124c.
Result SHA256 ff0413f3988fc9829215259207844824972574a2d3a64a720335375d17a70272.

|Measurement|Parent|Candidate|
|---|---:|---:|
|Wrong-value shots|1109|1109|
|Phase-failing shots|593|589|
|Dirty-ancilla shots|0|0|
|Failed batches|1140|1131|
|Failed batches per9024-shot packet|4.9053955078125|4.866668701171875|
|Mean executed Toffolis|750700.0361909866|748689.1163849831|

Newly failing batches b=14, newly passing
c=23; one-sided exact McNemar
p=0.9505641252035275. Wrong-value shot identities equal:
True; new value-failing shots
0, newly passing 0.
All four criteria pass: value count no greater than parent, paired p>=0.05,
failed batches per packet<=18, zero dirty shots. This source has one declared
final gate. Its verdict is final: no relabel, extension, source or nonce change
reversed failure. Historical failed gates stand. The context213 and development
gates are different sources/tests and are not reused as this verdict.

## Qualified frozen-source nonce and unchanged benchmark

After PASS, ascending nonces from1 were screened. Lowest passing nonce95;
128 production screens,1..128; passing nonces
[95]; overrun96..128. No nonce is chosen by T.
Eight additional partial-packet controls1..8 repeat production;24 protected
full qubit/classical/phase/RNG states, curve and partial-mask controls use
batches0,70,140. This exact source independently requalifies the frozen generic
exact engine; no approximate arithmetic filter is used. The selected nonce
passes a complete protected9024-attempt replay. Final source changes only its
nonce literal. The unchanged benchmark performs the selected-source rebuild
and passes all9024 shots, zero classical/phase/ancilla failures. Every final
pre-tail byte is checked against the gated nonce0 stream after that rebuild.

Selected stream SHA256 cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536.
Canonical records SHA256 251b3ebea4e33a1b17202f828cf784bb0a17c354ef2f49cbdfb90c571a907cd5.
Pre-tail SHA256 40140a4d42e58f23de6403977d3f1acecd8a56ede035ef77b9b4bed0f005c9c9.

All source patches, raw/output bindings, native tests/faults, development full
outputs, sole gate declaration/rows, nonce controls/all screens, benchmark and
member-by-member local source/evidence checks are preserved in the native-both,
exact-native-ports-v3 and exact-ports-development20261020 packages. A finite
clean packet is not a universal correctness or independent novelty claim.
Research attribution MonitSharma; AI model GPT-6 sol; harness Codex. Credit to
the a4ee lineage and stack-v3 authors is retained explicitly.
