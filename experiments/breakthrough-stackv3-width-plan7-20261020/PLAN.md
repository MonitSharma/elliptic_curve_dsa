# Explicit independently native-verified seven-wire dropped-carry plan

Recipe SL_N2_DROPN already selects2, so the prior drop2 override was a no-op.
Closed-ripple flags are empty; the earlier closed-path explanation was wrong.
Current fold_plan_d only admits budgets8/9. Add a new explicit50-bit/budget7/
drop>=3 case, using the already independently tested exact plan from prior
plan7 research: lengths7,6,6,5,5,4,4,3,3,2,2,3; nonadjacent drops0,2,4,6,8.
Its ladder is unchanged, all original drop/live-parent/cap assertions stay.
No old8/9 guard is weakened; unsupported cases still follow original rejection.

Retain exact loan128. Requestdrop3 at forward130 only in lowerbudget cases;
baseline1234 and fullpublic control use the original recipe. Port the exact
two existing native controls for full50-bit affine addition/phase/7-and8 width
and adjacent-drop rejection. Add direct new admission and missing-phase fault
controls. All4 must pass before any new full construction. Then fullpublic714c
must reproduce, followed by fixedraw1234/t21,1234/t28,1233/t28,1232/t28.
Stronger28-bit witness for candidates, no new approximation/guard/cut. Keep
all failures as construction results, no final gate/nonce/benchmark here.
