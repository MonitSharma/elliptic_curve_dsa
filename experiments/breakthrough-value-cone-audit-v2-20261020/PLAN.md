# Read-only dependency audit for possible exact value-only rejection filters

Parent public failure rates make ascending nonce search expensive. Audit whether
point outputs depend on random measurement outcomes and how much code exists
only for phase/cleanup. This does not alter a candidate or screen any nonce.
Classical writes get unique SSA versions; PushCondition captures the current
version even if that bit later mutates. Conditional reset/store preserves old
dependencies; all future guards are marked through the captured stack. Mark
all512 registered quantum outputs and conservatively retain every influencing
quantum/classical value operation. Phase gates excluded ONLY for value analysis.

Four native controls check full basis/guards/captured mutations/live and dead
RNG positions/conditional stores/resets/swaps and a missing-guard negative case.
Native internal slices preserve RNG draw positions and compare output values,
not phase or dirty ancillas. No slice is exported as a quantum circuit. Fixed
full publicacd0 and currentT71 streams/source hashes, protected simulator/curve
dependencies unchanged. No statistical gate, nonce rejection, benchmark or score.
A future filter would require independent exact qualification and could ONLY
reject proved wrong point values; full protected validation still decides PASS.
