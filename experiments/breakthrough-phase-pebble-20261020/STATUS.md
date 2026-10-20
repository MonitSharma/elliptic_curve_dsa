# Early carry erasure with direct phase repair

Three native component tests pass, including606208 small-basis evaluations
over the declared parity/constant/drop patterns, all physical measurement
coefficients on64 bases, inverse, exact executed Toffoli counts and width.
Nonadjacent dropped carries have their target sums written first; the next
carry is later erased using the two-stage phase kernel on the completed sum.

Each drop saves one clean carry. It adds one or two CCZ under its own HMR
outcome: expected0.5/1 scored Toffoli, with unchanged HMR count. This is a
component tradeoff, not a scored point-add result. The local completed-sum
identity is UNSAT; it does not formally verify Rust or full point addition.
All20 archive members verify locally. See LITERATURE.json for established
measurement-pebbling context; no novelty claim is made.
