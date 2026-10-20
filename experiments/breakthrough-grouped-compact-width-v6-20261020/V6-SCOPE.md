This replaces the historical phase-product strategy entirely. The new exact
comparison keeps m clean measured carries as a prefix. For each omitted tail
carry apply in-place MAJ(a,b,c): CX(a,b), CX(a,c), CCX(c,b,a). Its a wire becomes
the carry, while b and previous-carry operand values are reversibly transformed.
Apply the original three-CZ terminal MAJ phase, then undo each tail MAJ in reverse.
All operands and prefix carry values restore exactly before the original measured
prefix erase. Each omitted clean carry removes one forward CCX/HMR and adds two
unitary CCXs: exactly one extra native Toffoli per saved helper. No precision,
window, predicate, round or correctness cut changes. Maximum n-2 saved carries
leaves one original prefix helper; use only the minimum required by actual cap.
All 2k omitted R/HMR draws are replaced by HMRs on a knownzero carry.

Four independent native controls cover every small-basis case/each legal cut,
arbitrary wider inputs and source-aliased seeds, guards, all quantum/phase lanes,
every measurement outcome, same total RNG draws and strict lower peak. The
terminal phase fault must fail specifically at the phase contract; invalid
accumulator alias is rejected. Prior27/group/square tests and exact full a871
control precede complete lowercap1234/1233 attempts. This scope supersedes all
earlier one-/four-/twelve-carry polynomial descriptions copied from baseline.
Previous prototypes remain unchanged and their final outcomes are retained.
No statistical gate, nonce, benchmark or scored resource result exists here.
