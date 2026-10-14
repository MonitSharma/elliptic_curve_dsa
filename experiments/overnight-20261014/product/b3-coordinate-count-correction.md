# B3 coordinate-count correction

The first official candidate failure, shot249, has correct x and wrong y. An earlier summary incorrectly generalized that first-shot description to all fifteen failing shots and claimed the separate repacked tests introduced thirteen x failures.

Parsing the already preserved official paired counterexamples shows **13 x failures and15 y failures**. The repacked four/six-stage diagnostics have exactly those same coordinate counts. The associated MR/lane value-sensitivity inference is retracted. No benchmark, source, packet, native binary or phase test was rerun or changed. The exact full-state pairing, all9024 packet/transcript reproduction, fifteen classical failures, fifteen phase shots across fourteen batches, zero ancilla failures and upstream raw-body localization remain valid.

Official failing indices and coordinate flags are:

| Index | x wrong | y wrong |
|---:|:---:|:---:|
|249|No|Yes|
|382|Yes|Yes|
|845|Yes|Yes|
|2020|Yes|Yes|
|2272|Yes|Yes|
|4210|Yes|Yes|
|4850|Yes|Yes|
|6376|Yes|Yes|
|6469|Yes|Yes|
|6741|Yes|Yes|
|7395|Yes|Yes|
|7412|Yes|Yes|
|7640|Yes|Yes|
|8015|No|Yes|
|8033|Yes|Yes|

The paired collector now derives per-coordinate counts directly from logged observed/expected values. Stage reports and the four-stage receipt explicitly record this correction. Measurement consumption still differs between raw/Y42/guard/restore stages, so phase comparisons remain unaligned and do not establish an introduced phase defect. Finite value tests do not prove global measurement independence.
