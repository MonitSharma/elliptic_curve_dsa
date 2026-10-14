# Forward57 finite repair prototype: full builder failed

Status: **FAILED**, no complete generated circuit, no benchmark, no resource record.

The isolated C5 prototype changes `fold_window` to57 for every forward payload tick and leaves reverse ticks at56. This is a finite mitigation hypothesis for the certified missing-borrow case at tick104; it is not a universal field repair. Gate-inert body observers preserve the original assertions. The dedicated build binary ran with four build threads, one library thread and a16GiB limit.

The full builder stopped at the existing allocator fingerprint before forward tick111 (`src/point_add/leapfrog.rs:125`): observed16431645618484216012 versus recorded10576213583458271052. Exit101 is preserved. No allocator assertion was bypassed or reanchored. No complete `raw-body.bin`, `raw-cost.json`, or `ops.bin` was produced, so no complete raw or scored cost is available.

The exact source patch SHA256 is `a7e7d073e45fe72e95f8d2a2a8ebb0c9bdb57117888e192ec2020a25a335569b`; baseline is `c5bb1ec876db859a3f9f8a9052c140a145df834e`. The source/protected-file receipt and patch are `repair57-failed-receipt.json` and `repair57-failed.patch`. Full log and native/source hashes are retained under ignored `research-output/overnight-20261014/product/repair57/` and server `/home/hclau/ecdsa_research/overnight-20261014/product-evidence/repair57/`.

Separate actual104 primitive tests are pending. They cannot establish full builder success or a field-wide repair.
