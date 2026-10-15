# Exact carry deferral hypothesis

This is a new research pass, not a circuit result. The sole AND in a clean
target is delayed until its first active classically guarded read. A fresh
classical validity flag records whether it has been computed. No quantum
wire is added. The original measurement stays at its original position and
draws the same random word. Its one exact CZ phase twin runs only if the AND
was computed. If no read activated, the measured wire is zero and the
suppressed twin would otherwise introduce a phase error.

Admission is conservative: the target has no intermediate write or swap;
every read is guarded; the erase is unconditional and holds only the AND;
the outcome has one exact phase twin and controls no other operation; input
control values must be reconstructible by reversible Clifford conjugation
at every read, without using the target. Temporarily reconstructed hosts are
restored immediately. Selected sites may not consume another selected
target's changed value through a newly introduced host read. New classical
flags are initialized and cleared at unconditional boundaries.

Native tests cover all quantum/control inputs and both measurement outcomes,
dirty new classical scratch, and deliberately missing phase-twin guarding.
Whole-circuit state and phase comparison and a fresh census are required
before any record claim or screening. Iterating independent leaf sites may
expose more of a carry chain, corresponding to a generic version of the
public square's source-bound guard trees.
