# Absorbing the consumer boundary carry

The effective correction above bit13 can be written as
`Z=(addend>>13)+carry13`, removing a separate exported boundary carry.
Version26 verifies this nonlinear output contract on all2,097,152 primitive
assignments, with26 independent integer outputs and complete reconstructed
correction bits13..255. The low13 accumulator outputs are retained.
Both sign bands and every H bit are included; no higher-word overflow occurs.

For the complete primitive range `k=-7..70`, the old sign is1 exactly when
k is positive. Incrementing the four remaining U bits can carry into bit17
only for k=1..8. On those inputs the all-one17..31 sign band becomes zero,
the H field increments, and the39..255 sign band stays unchanged. Consequently
the interface retains separate signLo and signHi rather than assuming one
replicated sign after absorption. The H increment changes only bits0..3;
bits4..6 remain unchanged on every input. There are346,496 carry17 primitive
rows; these are truth-domain counts, not benchmark execution frequencies.

The direct source realization uses four U carry ANDs and three H carry ANDs:
45 ANDs rather than the previous38. Its source span is67. Raw rank22 and
target-inclusive rank46 still give a necessary24-AND value bound. No cheaper
arithmetic cancellation netlist was found, and this route is closed for the
research window without further resynthesis. Neither the bound nor the seven
added ANDs is a whole-circuit executed count. Phase cleanup, actual physical
consumer scheduling, all dirty scratch and a full score remain unqualified.
