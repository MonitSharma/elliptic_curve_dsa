# Physical common-control rewrites: terminal source-only negatives

Two distinct bounded source queries found no eligible sites on any of four
fixed streams: original4b, product25, product67 and our public Toffoli source5a.
No candidate was changed, no benchmark was run and no nonce was screened.

The first query looked for consecutive groups of at least three CCX with
identical controls and classical guard. Such a group could use a restored
dirty donor with two CCX and two CNOT fanouts, but every stream has zero groups.

The second query looked for same-target CCX pairs sharing one stable control,
outside Push scopes, with the same unchanged classical guard. It additionally
requires the earlier other control unchanged and the target unread, unmeasured,
unreset and absent from phase gates between the pair. These conditions permit
moving the earlier toggle to the later gate and factoring a(b XOR c), saving
one Toffoli without a new qubit. Again all four streams have zero eligible pairs.
These are strict physical-wire queries, not an exhaustive exclusion of broader
symbolic identities. No unsupported guard or donor relation was relaxed.

The frozen stream digests are checked before decoding each source. The decoder
uses the documented QECCOPSZ header and seven-u64 protected record layout,
bounded to20million records, and requires exactly the declared decompressed
size. Runtime is one core, with at most about1.2GiB resident in these scans.
Both declarations, complete source, counts, logs and terminal exits are retained.
All diagnostic savings are zero; there is no scored resource claim.
