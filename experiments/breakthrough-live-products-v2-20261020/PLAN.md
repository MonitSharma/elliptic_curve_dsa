# General exact live-product and affine-span elimination

Fixed complete input sources before sampling: publice3/714c, fixed1233/t28 generic
36e809, our officially reproducedT748691/cec715. Reuse the exact XOR/SymTriple
algebra from the controlled context engine, cap96 terms and fresh whole-function
atoms on overflow. Track all original operations, registers, mutable classical
values, fresh measurement outcomes and captured guards. At a CCX/CCZ, its two
control product may be exactlyzero/one or an exact affine parity of CURRENT
other physical quantum wires. Sparse atom closure (64 wires/3 levels) nominates
rows; Gaussian elimination over full exact symbolic expressions proves parity.
Replace only that gate with CX/X or CZ/Z of the proved parity, retaining its
classical condition and lexical guard. CCX may never use its own target as a
parity control. CCZ self-target factors becomeZ. No measurement, RNG draw,
classical operation, metadata or quantum index is added or reordered. Every
proof state consumes ORIGINAL operations before the next query.

Input constraints are only circuit register metadata/zero ancillas; arbitrary
quantum/classical data and measurement outcomes. Hashes index full keys only;
no fingerprint-based acceptance. Native controls must verify full basis/phase,
guard capture/mutation, self-target exclusion and broken affine relations before
any complete source scan. Static savings are not full benchmark results.
No final gate/nonce/benchmark; each assembled finished source needs its own gate.

V1 tests stopped before scans because the fixture helper validated register annotations before setting their register ID. V2 fixes only fixture construction and strengthens self-target/large-support/constant/omitted-row controls. The simplifier algorithm is unchanged. All five native controls must pass before scans. V1 source and original failed tests remain.
