# Exact two-stage carry-phase fusion

Four native tests pass. The pair uses no carry workspace and1 scoredCCZ
when either source XOR row is empty or both rows match; otherwise2CCZ.
The full phase ladder therefore saves one clean carry at zero extra Toffolis
for source-row rank<=1, or one extra Toffoli for rank2. All operands and the
exact carry/NOT-carry phase sign restore. Independent constant terms work.

Checks cover262,144 pair bases across every pair of four-source parities,
174,592 whole-ladder bases n2..6, each physical measurement-phase coefficient
on64 bases, and alias rejection before emission. Seven local Boolean
identities are UNSAT and a wrong-sign control is SAT. CCZ receives the same
scored-gate attribution as CCX; no protected harness change is needed.

All25 archive members verify locally. This is component evidence, not a new
algorithm novelty claim, complete point-add result or final statistical gate.
