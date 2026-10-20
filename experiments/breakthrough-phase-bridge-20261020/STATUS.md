# Complemented carry predicate with source borrowing

Three native component tests pass, including1,047,552 small-basis evaluations
(some selection patterns repeat), exact NOT-carry phase sign, arbitrary old
output bit, empty rows, physical measurement-phase coefficients on64 bases,
and unsafe-admission rejection before emission. Four local Boolean lemmas
are UNSAT; the wrong-sign control is SAT. These do not formally verify Rust
or complete point addition.

Original fixture failure is preserved: an untouched output spectator was
missing its register declaration when every carry was borrowed. V2 adds only
that test declaration; runtime arithmetic bytes are unchanged. All37 archive
members and17 protected files verify locally. No point-add integration,
final gate, nonce or resource record is claimed.
