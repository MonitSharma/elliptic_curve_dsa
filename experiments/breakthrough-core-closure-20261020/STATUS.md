# Legacy helper synthesis: exact model result, inactive in the submitted circuit

The restricted product-closure search found an 18-product construction for
the older 19-product `addend_from_n` helper. Independent truth-table checks
cover all 256 inputs, including the native exceptional behavior at -128.
The pure 16-product subspace closes below the target in the specified Boolean
XOR/AND straight-line model. The selected lifted subspaces do not establish
a general 17- or 18-product lower bound, or a quantum lower bound.

Activation audit: the submitted recipe enables `Y15_CORE_V2` and `Y16_CORE`.
Its forward and reverse tables use 14 and 12 products, respectively. The
legacy helper is reached through disabled branches. Therefore the new
18-product model is **not an improvement to the active circuit**. No native
18-product circuit, full point-add result, final gate or nonce search is claimed.

The separate active-prefix study independently matches all 31 live helper
functions, 21 fields and eight derived bits on all 16,384 source assignments.
