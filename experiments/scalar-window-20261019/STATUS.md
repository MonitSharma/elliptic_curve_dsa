# Larger exact public-input tables — isolated component benchmark

Declared before run. The active search uses the previously validated unsigned
window20 backend. Copy its source and change only the accepted width upper
bound20 to24. The fixed-base digit decomposition, table construction, group
arithmetic, scalar reduction, curve, packet and active library remain unchanged.
Test predetermined cases frozen20 and extended20/22/24, one process at a time.

Require all655360 fresh synthetic public scalar pairs per variant to produce
exactly the frozen reference's P,A,P+A bytes. Five distinct131072-pair corpora
avoid small repeated-cache lookup tests. Include single-bit/complement/extreme
scalars and partial batches. Record startup, peak memory and timing. No nonce
packet or new candidate is tested. This is not a complete-search speed gain.

Window24 reserves roughly12GiB of immutable table plus temporary construction
arrays;32GiB per-process cap, one core, sequential cases, with inspected244GiB
available. The existing validator has already passed its resource admission.
Never modify an active library or process. Any production change still needs
exact input/reference, full source-specific runtime/prefix/cost qualification
and multiworker memory admission after rechecking actual resources.
