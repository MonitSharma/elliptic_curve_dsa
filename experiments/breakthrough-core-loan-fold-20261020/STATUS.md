# Complete forward fold passes; full raw circuit remains noncompetitive

The new full-fold test and 19 retained controls pass. The complete fold is
checked on all 16,384 small-core inputs with independent upper words, five
tight budgets, both TT modes and three guards, plus all measurement/reset
positions on the larger fixture. Outputs, phase and clean workspace match
the original. All tested new folds fit cap 1,233 versus control cap 1,234.

The complete raw point-add circuit has peak/touched width 1,233 and stream
`6b375c3a6e3e08cd3d67f7113d443e32976eeedb9c0e4a326019759da6ea77ec`.
The control remains byte-exact `13f6ffc3`.
Raw builder expected Toffolis are 764,011.8, up 40 versus the preceding
1,233-qubit prototype and up 1,781 versus raw control. These construction
diagnostics are not executed benchmark scores. No product improvement,
full correctness census, final gate, nonce search or submission is claimed.

The production policy activates 22 times. A separate experiment tests
borrowing only the helper count needed for the target ladder budget.
