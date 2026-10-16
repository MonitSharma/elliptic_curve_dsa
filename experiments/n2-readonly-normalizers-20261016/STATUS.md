# Source-only read-only control query

The fixed all-source query is terminal. Allowing quantum controls that are read
but never value-written expands the strict 650-wire pools to 653 in divide and
652 in multiply. Classical controls are restricted to slots never written in
the entire loan interval. All 16 dirty targets and both source loans were queried.

No exact affine or existing inverse-product expression closes any of the 12
nonconstant dirty targets. Four bit4 targets remain exactly zero. One additional
stable product is available in divide, but it does not close a dirty target.
This is a bounded negative result; no exhaustive pair or higher-degree search
was attempted. No circuit or input sample was generated.

Four query/algebra tests pass. The retained kernel and its 512-atom/200000-product
limits are unchanged. Before/after source hashes match. The query took 16.83 s
on one core with peak resident memory about 1.13 GiB, under the fixed 16 GiB cap.
The narrower strict-650 negative remains preserved separately.
