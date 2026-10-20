# Test the square-stage budget independently

Both raw1264 and the fixed two-bit stronger late-comparison variant are
nonqualified in512-batch development tests against the exact public Toffoli
parent:49vs16 and48vs20 wrong-value shots respectively; dirty0. Original
evidence and labels remain. No final gate has been declared.

The wider sweep deliberately retained LF_SQUARE_CAP1234 from the width work.
The public parent's square uses its wider global budget. Test fixed1264 global
and hard budgets with square1264, both the original and stronger late comparison.
Freeze these three cases before generation: control(strength0,square1234),
square(strength0,square1264), strong-square(strength2,square1264). No profiles,
tables or cuts beyond the previously declared stronger variant change. The
square uses its existing budget-dependent algorithms; no assertion is relaxed.
Control must reproduce7fe2bb94 exactly. Generation and expected counts remain
diagnostic. Use fresh declared development inputs only after the complete source
and streams are frozen; a final gate still requires a competitive admissible
candidate and the exact current public parent. No nonce or packet tuning.
