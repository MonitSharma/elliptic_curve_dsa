# Missing native test setting, not an arithmetic verdict

Original27 exact controls and groupedplan control passed. The G3 unit clears
its environment before installing supplied pins; its old driver forgot to put
PEBBLE_HARD_CAP in those pins. It stopped at phase_fit::cap NotPresent during
construction, before simulation. Preserve originalrun.exit1 and all logs.

Resumed unit pins set PEBBLE_HARD_CAP1536 (the unchanged currentT constructor's
own value), with local square phasecap1408, and repeat all three square unit
cases and the deliberate junction fault before any full construction. No
source/freeze/precision/label changes. All native input batches remain fixed.
No statistical gate or nonce exists for this line. Completion is resumed.exit.
