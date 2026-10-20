# Native fixture settings supplied before a new source freeze

V1 original run stopped at deliberate-fault fixture because its pins omitted
PEBBLE_HARD_CAP. A separate resumed driver restored that missing setting on
unchanged source and same fixed inputs: intended fault detected122 wrong outputs
and43 phase failures/128shots. It then stopped at the new leaf roundtrip because
that historical unit clears environment internally and omits the same independent
phase-cap setting before construction. Originalrun.exit1/resumed.exit1/logs stay.
Neither failed fixture reached a leaf arithmetic simulation; no point generation,
statistical gate or nonce ran. All five new full square callers and prior27/group
controls had passed. Original outcomes are not rejudged as passes.

V2 is a new frozen source: add PEBuilder1536 ONLY in cfg(test) sqleaf_unit after
its environment clear; retain all production arithmetic source and every guard.
Correct the fault-driver pins before launch. Repeat all prior controls, six full
square callers, independent deliberate-fault detection and six leaf roundtrips,
then unchanged fulla871/dc1478 controls and fixed grid. No seed/batch/window/round
changes, no packet tuning. Failed setup fixtures do not count as arithmetic or
statistical gate verdicts. No scored result until full independent verification.
