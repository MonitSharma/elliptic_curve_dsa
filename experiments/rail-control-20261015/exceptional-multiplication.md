# Proposed treatment of the zero multiplication operand

Status: algebraic design only; no candidate circuit or score. The exact finite
identities are checked by `analyze.py` on all 128 fixed P=-2A inputs.

For variable point P=(x,y), classical offset A=(a,b), and x != a, write

    slope = (y-b)/(x-a) mod p
    u = x + 2a - slope² mod p
    output = (a-u, slope*u-b) mod p.

When P=-2A, u=0 and slope=3a²/(2b) mod p. This slope depends only on the
classical offset. The current nonzero-operand multiplication walk assumes
coprime rails and cannot be used unchanged at u=0. Enlarging its rail schedule
cannot establish that missing precondition.

A possible reversible extension would compute a quantum flag for u=0, map
that operand temporarily to one, run the ordinary multiplication, and on the
flagged branch XOR the classically computed tangent slope out of the y
register. The temporary operand and flag must then be restored/uncomputed.
On valid curve inputs the exceptional branch gives y=0 before the final -b.
The XOR is a reversible physical operation; it must not be implemented as a
measurement or unconditional reset of the slope register.

This design still needs an actual implementation and proof. Physical zero may
be represented by either 0 or p, and the present seed and coordinate seams
alter the physical register before/after multiplication. They must be observed
and handled explicitly. Disabling seed fusion and using a separate final
coordinate subtraction is one possible integration baseline. A circuit for the
tangent slope must operate on the runtime classical input bits; substituting
sampled values or externally computed test answers is not acceptable. Its
operation count, memory cost and classical scratch must also be measured.

The separate zero-slope family has u != 0. Its inherited division phase errors
and square representation defect require their own repairs; this proposed
exception treatment does not solve them. The square contract is currently
being integrated from the independently tested earlier research.
