# Constructor interfaces with fewer retained helpers

These are exact primitive value-interface probes on c5bb1ec8, not qualified
point-addition records. Each truth vector covers all 16,384 assignments to
acc0..5, E0..2, Nm0..2, k1 and k2, including primitive assignments whose
admission by a full arithmetic producer has not been established.

The original constructor uses 31 ANDs. Raw affine rank is 15 and the complete
retained-value target rank is 40. The previously established lower bound is 26,
with no claim that 26 is attainable. Fewer auxiliary directions could reduce
both construction and cleanup cost if a complete circuit were found.

## Completed selected families

The [v8 receipt](minaux-interfaces-v8-summary.json) covers all 89 distinct
external cosets represented by the 91 raw-coordinate products: two products
already lie in W40. Each candidate has rank 41, a 26-AND value budget. All 89
closed negatively: 88 exact quadratic-span obstructions and one trusted solver
UNSAT for TT = k1*k2. Every terminal prefix has 9 ANDs and span rank 24.

The [v9 receipt](minaux-seedproducts-v9-summary.json) uses that exact reachable
S24 for W40+TT. Of 276 basis-pair products, 33 lie inside W40+TT and the remaining
243 represent 236 distinct outside cosets; 148 involve a constructed basis
operand. All 236 rank-42 candidates, with a 27-AND value budget, close with
trusted affine-product UNSAT at 10 ANDs and span rank 25. No unknown remains.
Arbitrary products of affine combinations and other auxiliary functions are
outside this selected family.

## Obstruction-guided partial construction

The [v10 exact description](symplectic-interface-v10-description.json) saves the
full 53-dimensional quadratic relation kernel of S24 modulo W40+TT. Fifty-two
basis relations evaluate inside S24; one gives a new direction in W40+TT.
Its alternating matrix initially has rank eight. Toggling one saved known
relation lowers the rank to six; this is a constructive reduction, not a
minimum-rank proof. Symplectic elimination gives three explicit affine
products. Their XOR, up to a saved affine correction, equals the new direction
on all 16,384 inputs. Two independent outside directions expand the interface
to rank 43, a 28-AND value budget. Two of these products lie outside the
original V46, so this proposal is distinct from the old fixed-span searches.

The 12-AND prefix independently replays exactly. The
[v10 completion receipt](symplectic-interface-v10-summary.json) nevertheless
finds no next affine-product extension at its span rank 27, by trusted solver
UNSAT. It therefore rejects this selected interface, not every symplectic
decomposition or all 28-AND constructors. No complete value witness was found.

The [v11 family receipt](symplectic-family-v11-summary.json) expands that single
relation using deterministic elementary symplectic transformations of its six
forms. All 256 selected, exactly deduplicated rank-43 outside planes close
negatively at 12-AND prefixes: 184 exact quadratic-span obstructions and 72
trusted affine-factor UNSAT results. No unknown remains. The 295 deterministic
trials preserve the complete alternating matrix and all 16,384-row product
identities. This is a bounded selected family, not every symplectic transform
or every rank-43 constructor interface.

The [v12 exact query](two-product-extension-v12-summary.json) asks for two
arbitrary affine S24 products whose XOR extends S24 inside W40+TT. It covers
all rank-at-most-four representatives modulo the known quadratic relations,
and returns trusted UNSAT. Its 43,414-byte SMT query is preserved by hash.
Two thousand independent random affine quadruples additionally check the
223 exact equations against full truth vectors. This excludes a parallel
two-product extension from this S24, with sequential uses of new products and
other reachable subspaces still outside the query.

All five jobs completed with exit zero, one core and a 2 GiB limit. Raw logs,
settings, PID/exit records and complete solver receipts are preserved in the
ignored research-output directory with hashes in the compact receipts. Solver
UNSAT results have no saved formal proof certificate. No cleanup, arbitrary
higher-coordinate arithmetic, native phase, complete stream count, width or
official score follows from these value-interface results.
