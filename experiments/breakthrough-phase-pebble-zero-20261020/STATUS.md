# Zero-input-carry phase-pebble adapter

Three native component tests pass in v1 and strengthened v2. V2 adds fully
enabled enumeration alongside the original mixed classical guard, changing
no runtime bytes. The first carry is held while bit0 is written; the live
carry primitive runs above it, then carry1 is erased from add0 AND NOTsum0.
The ordinary adder's CCX base and HMR count are preserved; carry-birth hook
indices shift correctly. Source/target aliases and empty first literals
reject before emission.

Full small n6..8 schedules, shared/empty parities above bit0, independent
constants, mixed/false guards, inverse, physical RNG coefficients, actual
width and executed Toffoli counts pass. No full point-add score or final gate.
