# Uniform positive-bias square primitive

The [source patch](positive-bias-small.patch) implements the uniform `x²+2`
producer hypothesis in a separate clean-base checkout. Its
[source/protected-file receipt](positive-bias-small-receipt.json) records exit 0
and no protected changes. This is a component result, not a point-addition
benchmark or resource record.

The old leaf produces the wrapped `x²-2` word. Exact full-word addition of 4
after its forward circuit gives `x²+2`; subtracting 4 before its inverse returns
the precise old word, including inputs 0 and 1. At a node, b²'s constant bit 1
stays cleared through assembly, so the retained cross is exactly `2ab` and
the product is `x²+2`. After deassembly the inverse restores t²+2 from raw b²
and a²+2, then restores b²'s bias before b's inverse. Full assembly is used.
The constant offset model returns 2 for every node. Row-zero copy remains
enabled; no coordinate normalization or nonce change is used.

Three native tests passed. Exhaustive leaf inputs for widths 3–8 cover
32,256 cases; exhaustive node inputs for widths 6–10 cover 126,976 cases:
**159,232 cases** total. Each width uses default and tight plan caps, 32 fixed
measurement patterns, a dirty XOR output consumer, every final quantum slot,
zero final phase and two untouched classical input sentinels. Measurement
scratch retains legitimate random outcomes and is not claimed zero. A deliberate
missing-bias fault is detected at input 0. The 32 measurement patterns are
finite native coverage, not an all-measurement proof.

The square source SHA256 is
`6715a4d2c1938155e7c2b2fc7299e736435369a8cf14d9d8607a7f93b842550d`;
the test source is
`b28d922fe4cb48de518a799d9b750048cf5ae72d066018382cf08cc6b769c780`;
the dedicated native test binary is
`ba82e3587cb3d3e69ef70d9a30e8b69245430c0b1b22a8df07419d82bc464bc9`.
All source is under `src/point_add/`; no scorer/harness/Cargo/history change.

Squares have bit 1 clear, so `x²+2=x² XOR 2`: bits 0 and ≥2 retain their unbiased
values, while bit 1 is the explicit constant. This restores the intended
nonnegative cross and higher zero-bit bounds even on zero/one limbs. Cross-bit-2
loans still contain old offset-4 handling and remain off, as in the fixed
production recipe. Production-sized real-borrow fixtures and all-measurement
checks for fixed inputs follow separately. Division's zero-slope phase error and
the `P=-2A` generic multiply obstruction remain unresolved.
