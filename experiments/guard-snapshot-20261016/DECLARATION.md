# Guard snapshot restoration: proof component only

Parent semantics are the unchanged protected circuit and simulator. This is
research tooling, with no generated point-add candidate, source selection,
fresh census, nonce search or resource claim. One build/test thread; no change
to the product25 production search or frozen circuits.

Question: after the last use of a cached AND inside nested mutable classical
guards, can cleanup execute globally and then restore the exact previous guard
stack? At every original Push(b), zero a distinct private classical snapshot
at the global prefix, then set it to one under the original parent scope AND b
immediately before the original Push. The snapshot equals that scope's combined
guard at entry, even if b is subsequently overwritten. Keep snapshots immutable
until a global suffix clears them.

At a proposed cleanup boundary of depth d, pop all d scopes, execute the
independently certified cache cleanup under its private valid flag, and push
the d saved combined guards in ancestral order. Their nested products equal
the original combined guards by Boolean idempotence. This component verifies
only snapshots, scope restoration and protected semantics; it does not certify
cache products, donor availability, HMR cleanup or a profitable source proposal.

Before a generator: require a source-only donor/proposal census, independent
raw-product/phase/cache lease proof, exact lifetime/guard snapshots, classical
index bounds, native source reproduction, fresh gate and measured search cost.
The earlier LCA-scoped cache result is marginal, not zero: about9--10 T on the
product source. Its source proxy greatly overpredicted savings. This idea must
clear actual measured gates independently.
