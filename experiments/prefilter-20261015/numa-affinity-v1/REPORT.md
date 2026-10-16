# Disabled NUMA-affinity comparison: no robust node3 win

Frozen disabled product-dispatch-filter binary SHA256fa676f130fdeae547c8e40eb7fd20375d1058c5285609c93f4a3e8e9155f3356; candidate25 source180af069; FAST_ZERO_DISPATCH absent in both environments. Three predeclared paired4096-nonce trials use4threads,first1,look4096, alternating mode order. Every complete sorted JSON row matches the frozen disabled reference d4118048 and all paired runs; all proof/authoritative-rejection gates remain false.24576 repeated timing attempts cover4096 distinct nonces, not an operational search.

| Trial | Unbound seconds | Node3 seconds | Bound/unbound |
|---|---:|---:|---:|
|0|17.630565|20.045435|1.136971|
|1|17.396406|18.275030|1.050506|
|2|18.960988|17.394621|0.917390|

Medians:unbound17.630565s,node318.275030s,ratio1.036554. Bound median is about3.66% slower; paired results vary in both directions. This is a bounded negative under the existing concurrent load, not a universal claim about NUMA affinity. No active worker affinity or production library/source changed.

The new isolated bound processes use numactl --cpunodebind=3 --membind=3, CPUs54-71/126-143. Captured child CPU masks match; maximum recorded resident-page samples are~99.9% onnode3. The identical separate policy probe reports bind/membind3. Mems_allowed_list remains the cpuset allowance0-3 and is not the per-process numactl memory policy. Unbound parent policy/default and all144CPUs are checked before launch. Resource preflight found261GiB available and~62GiBnode3free, with60 aggregate agent compute threads including this4-thread job. Separate unrelated lattice jobs were left untouched.

Reported wall_seconds measures the frozen tool's work section after initialization. Subprocess durations include initialization, output parsing and up to2seconds polling overhead, so they are not a separate steady-state comparison. Inputs, source binary and model hashes are unchanged before/after. Raw resource/process inventories remain server-only hash references; complete outcome rows, declarations, scripts, receipts and locality samples are archived. The runtime is terminal and its4-thread budget released.
