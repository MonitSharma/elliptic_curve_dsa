# Wide cache transfer: first candidate does not qualify

15 October 2026. Porting the exact cache with expression/product caps
128/1000000 to our official source `5a7c3902` saves **6.43 ± 0.75 T** in a
4096-batch paired census. It does **not** reproduce the ~101 T saving measured
earlier on B3. There is no new benchmark pass or record; no nonce was screened.

The circuit grows from Q1464 to Q1468, with only seven cache groups. It keeps
the earlier passes and their symbolic limits unchanged: the final pass uses a
separate support module. Both native tests pass, including the phase-fault
negative control. An independent emitter reconstructs the candidate operation
stream from the parent and the logged leases. Event-aligned replay agrees on
all quantum values, original classical bits and phase, with clean new scratch,
on 256 independent and 256 structured inputs. The inherited 128 structured
wrong values and four phase batches are preserved in that replay.

| Diagnostic census, same label | Parent | Candidate |
|---|---:|---:|
| Shots | 262144 | 262144 |
| Failed batches / 4096 | 159 | 161 |
| Expected failed batches / packet | 5.4734 | 5.5422 |
| Wrong-value shots | 142 | 142 |
| Phase-failing shots | 85 | 94 |
| Dirty shots | 0 | 0 |
| Mean executed T (not a score) | 753764.696 | 753758.266 |

The qualification gate stopped on the census and savings checks. It did not
launch screening. The small unaligned phase-count difference is not evidence
of a new semantic error; the aligned differential agrees, but the measured
candidate does not meet the stated failure-rate gate. No input or packet was
used to choose cache contents. Larger structural discovery limits are being
tested separately; they have no qualified result yet.

Source, stream hashes, patch and full logs are preserved on the server at
`/home/hclau/ecdsa_research/wide-cache-20261015/`. Launchers and summary code
are in this directory. Evidence collection is in progress.
