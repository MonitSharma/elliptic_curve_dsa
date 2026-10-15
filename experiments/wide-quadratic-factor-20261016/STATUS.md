# Same-target distributive factoring: bounded source negative

The predeclared source-only scan finds **zero eligible pairs** on the official
753721/Q1468 stream1d8c05ee, corresponding to public sourceb5adb653. It inspects
all10522755 operations, including773580CCX gates. Only five untouched-target
repeats reach endpoint checks: two exceed the fixed64-intervening-op limit,
and three do not have exactly one common control. No window retuning or
alternative ranking follows this negative. No candidate or sample was created.

Three costed exact hypotheses were documented before launch in
`HYPOTHESES.md`; only same-target two-product distributivity was selected.
The proposed complete identity would save oneT per executing guard and add
twoCX, with noQ/MR/classical slots. It does not borrow/cache a repeated product.

Admission is deliberately strict: the target has no intervening read or write,
including every phase/measurement use; all three distinct controls retain
their values; direct classical condition versions agree; captured Push guards
retain their snapshot values; scopes and register/debug boundaries are fences.
Conditional writes conservatively advance value epochs. Thus a second CCX
could commute to the first without crossing a target observation or a control
change. Reversible CX conjugation produces the exact different-product XOR
and restores its scratch control immediately under the same guard. This is
an arbitrary-dirty-target permutation identity, preserving any initial phase
and entanglement, with every original MR event in place.

The unmodified scanner passes12 synthetic source controls, including positive
cases, target phase and HMR reads, both old/new control writes, changed direct
guards, mutable current bits behind captured guards, scope fences and both
sides of the64-op distance boundary. The exact identity is checked on all32
four-wire-basis/guard combinations. Main/controls exit0. Source scan took24.97s
elapsed, one core,656640KiB peak RSS under16GiB; PID407396 is terminal.

This negative covers only the declared physical stable-control family and
bounded window. It does not rule out affine-control resynthesis, majority
cones, cofactors or a broader proved commuting relation. None was selected
after seeing these results. Historical cache/fanout/global-LCA/disjoint-endpoint
negatives were read and are not rerun here. Active searches and source trees
are unchanged.

Exact input remains immutable at
`/home/hclau/ecdsa_research/wide15-record-20261016/evidence/final-ops.bin`,
SHA2561d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77.
The pre-existing wide15 archive retains the complete producing source; this
small supplement hash-references that archive rather than duplicating its
33015874-byte stream. Every new script/control/result/log is archived here.
