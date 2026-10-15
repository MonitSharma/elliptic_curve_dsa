# Rail signed64 suffix: complete advisory component

The isolated specialization is terminal PASS. It keeps the original generic
five-limb prefix and runs only the final28 of138 ticks in signed64 lanes,
starting at tick110. The frozen table's suffix widths are all<=60 and
monotonically nonincreasing. A full-suffix<=61 predicate conservatively handles
other valid tables without requiring monotonicity. `PROOF.md` gives transition,
signed sum/negation bounds, every shift/window bound, overflow-mask preservation,
captured predictor behavior and final representation correspondence.

The new library SHA256 is
`d53b31adb2fe3a22da15a1fb21531951566f663d9452f165a01d403eb5edaa32`.
The generated source SHA256 is
`4222011eb6f2bda2ab3fe95352623709d1e9f324811348a21b0b5a4aad20c655`.
Baseline library is frozen046dd5f1d11386550ec5234b955f6bc1974431e79a6b80499bda97da0ade3e90.

All262144 original population flags match both the frozen baseline and the
existing original reference flags. All517 old edge inputs and partial lengths
1,3,7,8,9,517 match. Changed valid/nonmonotone tables, large anchors, shortened
tables, invalid widths and empty tables preserve results/return codes. The
literal original generic loop also agrees on14336 arbitrary-sign lanes at
every actual suffix start; synthetic controls add2928 lanes covering all signed
widths1..61 and anchors0,61,319. A wrong logical-shift sign-extension library
fails all366 synthetic packed cases. Main and extra-control exit markers are0.

Three predeclared interleaved full-population component trials, seconds:

| Trial | Frozen046dd | Signed64 tail |
| --- | ---: | ---: |
| 1 | 2.160254115 | 1.239059129 |
| 2 | 1.458449457 | 1.384788222 |
| 3 | 2.039964068 | 1.238211346 |

The median is7.78185 versus4.72664 microseconds/shot (1.646x), while the
best-to-best ratio is only1.178x. The wide baseline range makes the median an
unstable speed estimate under the co-running server workload. No end-to-end
preparation, operational-cost or search speedup has been measured or claimed.
The main verification used66.8MiB peak RSS and11.41s elapsed; all work was pinned
to one core with a16GiB virtual-memory cap. Extra controls PID387855 is terminal.

This is advisory-only infrastructure. No circuit, proof-bound filter runtime,
search worker, nonce selection, production library or active job was changed.
Root independent review and a separate integration/cost protocol would be
required before any operational use. The prior full138-step unrolled negative
was not repeated.
