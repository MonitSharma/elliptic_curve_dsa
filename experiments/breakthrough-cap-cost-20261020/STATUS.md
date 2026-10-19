# Raw-arithmetic capacity admission study

Negative admission result; no reduced-width circuit or scored result.
The predeclared capacities were1234,1200,1168,1136,1104. Raw cap1234 exactly
matches every serialized operation byte of the admitted baseline prepass.
All four smaller settings fail native generation because pinned payload-fold
and carry ladders do not have enough scratch. For example cap1200 reaches
forward tick97 with room14 where39 is required; cap1168 fails a forward fold
with budget6 and active1164. No failing generation is a resource result.

Original failed admissions are preserved: the first compared differing zstd
framing, and the second reader passed a buffered file descriptor at the wrong
offset. The corrected unbuffered reader proves identical header and all
630743288 decompressed bytes without regenerating the baseline or changing
source. These are diagnostic tooling repairs, not statistical gate reruns.
All17 protected files remain unchanged. The51-member evidence archive has
been verified locally. Full baseline stream remains on the research server.
