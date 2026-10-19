# Exact advisory sign-extension experiment — not a circuit optimization

Declared19 October2026 before running. The mandatory ascending nonce search
is the long remaining step. Investigate speeding its frozen advisory kernel
without changing the circuit, input packet, model/step tables, masks, witness
verification, active library or active search. No nonce is tested here.

Replace only sx: preserve low complete limbs, sign-extend the one partial limb
with a left/arithmetic-right shift, and fill higher limbs with its sign. This
is exactly320-bit two's-complement truncation/sign extension for widths1..319.
All other kernel source stays byte-identical; append the same test-only probe
to baseline and specialized research copies. Preserve original library hash.

Require independent scalar/baseline/new agreement for every valid width on
single-bit, single-clear-bit, alternating, extreme and fresh synthetic values;
invalid widths must reject. Full advisory flags must match the frozen reference
population, adversarial denominators, partial vectors and changed step table.
Use five alternating-order timing trials. A microbenchmark speedup is not an
end-to-end search gain. Any later operational use requires a separately bound
disabled runtime and full seed/state/phase/RNG/prefix/cost qualification.

One compiler/core,8GiB cap. Keep the current census and60-slot search intact.

## Completed evidence checkpoint

Exact sign-extension experiment:287100 primitive cases, all widths1..319,262144 frozen advisory flags and517 adversarial/partial/changed-table cases match. Dynamic-index v1 is correct but slower (0.560x). Fixed-branch variant gives1.173x kernel median. Complete-prefix evidence is mixed, so keep the active runtime unchanged. No circuit, new-source nonce or score.
