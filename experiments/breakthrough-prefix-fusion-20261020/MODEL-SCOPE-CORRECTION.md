# Original-input interface rank

The initial interface enumerator asserted an11-dimensional nullspace, carrying
over the final input-basis rank from the prefix workspace model. It failed
before any search ran. The original-input frame also requires the low-sum
carry contributions:its required helper coefficient rank is25, leaving a
6-dimensional nullspace and63 codimension-one retained spans.

The failed enumerator is retained as interfaces-failed-rank-v1.py. V2 derives
the dimension from exact elimination rather than assuming11. The first12
sparse interfaces and the separate complete63-interface run both use the
correct rank. Their sparse-factor failures remain incomplete searches, not
global AND lower bounds. No native circuit, final gate or resource record
comes from these models.
