# Separate product research, 15 October 2026

This chat owns product research in `experiments/product-focus-20261015/` and
`/home/hclau/ecdsa_research/product-focus-20261015/`. The other chat,
"Run ECDSA.fail research cycle", owns the 692-qubit profiling/submission work.
Its checkout, processes, evidence, and shared summary documents are not edited here.

The refreshed public product is 939,396,074. At 1,234 qubits the strict target is
at most 761,260 rounded mean executed Toffolis. See `public-frontier.json`.
Our passing historical C5 baseline is 761,658: a material reduction of at least
398 rounded Toffolis is needed. Its finite pass does not erase the documented
independent-input failures. No nonce search or sampled absent-control removal.

First experiment: census measurement-based uncomputation after the immutable
fingerprint-bound rewrites. This changes the cleanup method rather than narrowing
arithmetic precision. Initial census is external and unscored. Any useful sites
need premise proofs, classical cleanup, native phase tests and a complete final
benchmark before a resource claim. Four build threads, one runtime thread, 16 GiB
virtual-memory cap, detached jobs with logs and PID records.
