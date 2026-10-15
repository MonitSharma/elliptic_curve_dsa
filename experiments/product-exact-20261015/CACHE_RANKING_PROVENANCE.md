# Cache ranking provenance

The start/proxy ranks used for product67 and the fixed95 continuations use
source structure and an analytical probability approximation only. For each
CCX at condition-stack depth d, assign w=2^-(d+g), where g records whether an
explicit classical guard exists. For a proposal, the proxy is
sum(w_i) - (1-product(1-w_i)). It assumes independent fair guard events;
actual guard values are never sampled for ranking.

Start sorts by source start, end and use indices. Proxy sorts by descending
proxy with the same lexical ties. Density sorts by proxy divided by source
interval length. Symbolic identities, zero donors, source touch/control fences
and nonoverlapping intervals determine eligibility. These heuristic scores do
not prove equivalence; the independent symbolic/gadget audits do that.

The optimizer does not read packet values, measured T, failure flags, sampled
curve inputs, nonce outcomes or census rows. The separate67/95 schedules and
endpoints were frozen before their measurements. Reported checkpoint counts
do not feed back into an in-progress recipe or choose an earlier endpoint.
The JSON binds the actual executable and archived allocator source snapshots;
the full flags-tool source is also retained in the evidence archive.
