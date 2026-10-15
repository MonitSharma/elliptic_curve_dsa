# Immutable guard snapshots and global cache cleanup

The snapshot/stack lemma below is proved algebraically and checked against the
unchanged protected simulator. The subsequent cache discussion states the
obligations for a future renderer; it is not a certificate for a generated
point-add circuit. No such circuit is present in this experiment.

For one bit lane, let S0=1. At the ith active lexical ancestor, the protected
Push stores its current parent mask and sets Si=S(i-1) AND bi, using bi's
value at that exact operation. Future writes to bi do not change the stored
mask. Allocate a distinct private snapshot si for each static Push, clear all
si globally before the circuit, then execute `si |= bi` under the parent scope
immediately before the original Push. As each static Push occurs once, si=Si.
This includes inactive scopes, measurements, reused classical guard bits and
guards that are functions of arbitrary input and earlier measurement results.

At a boundary inside d scopes, pop all d scopes. The current mask is now1.
After an independently justified global payload, re-push s1 through sd.
The reconstructed mask at level i is product(S1,...,Si)=Si: for j<i, Si*Sj=Si
by Boolean idempotence. Thus every current and saved ancestor mask is restored,
including those reached by later Pops. All original quantum, classical, phase
and measurement semantics after that boundary are identical. This is a
pointwise identity, with no assumption that guards are independent or static.
Clear all private snapshots globally at the circuit suffix. Required framing:
balanced source scopes, unique/disjoint snapshot IDs, no other snapshot writes,
and prefix/suffix outside every original scope.

The protected test uses an identity payload with two CCXs specifically to
measure that the temporary scope is global even when all original guards are
false. Those two test gates are not proposed as circuit optimizations. It
checks69,120 packed cases /4,423,680 lanes, depths1--8, every instruction cut,
arbitrary dirty quantum/classical entries, BitInvert/Store0/Store1/HMR guard
writes, phase probes and subsequent guarded Toffolis. All original state,
phase and draw positions match. Private bits finish zero. Restoring mutated
original bits instead of saved snapshots fails55,880 controls. Exact Boolean
ANF checks4,160 equalities through depth64; the induction above is general.

A future cache renderer can use this lemma immediately after a lease's last
use, before a later control write. It must separately prove that its borrowed
donor is zero at lease entry, untouched except harmless original zero resets,
and that every cached use has exactly the same Boolean product F. A private
valid flag starts0, computes F into the donor on its first active use only,
and records that event. Each replaced target then receives a CX from the donor.
For a active old uses, the old executed cost is a CCXs and the cache cost is
1[a>0]. Saving a-1[a>0] is nonnegative without independent-guard assumptions.

At global cleanup, the donor equals valid*F. An HMR under valid contributes
phase valid*F*m and resets the donor. A CZ of the certified cleanup controls,
under valid AND the new measurement bit m, contributes the same phase and
cancels it. Reset private flags and restore the saved scopes. This needs an
independent checker for every actual product, donor lifetime, condition and
physical operation, including preservation/projection of original MR events.
The stack lemma alone establishes none of those source-specific premises.

Classical snapshot storage does not add logical qubits, but its IDs and the
complete final classical width must fit every runtime's actual integer type.
Never truncate a width above65,535. Actual fresh failure gates, source-bound
native generation and unchanged final benchmarks remain mandatory. The old
LCA-scoped cache's source proxy greatly overpredicted its measured savings;
new proposal counts must not be published as gate or product records.
