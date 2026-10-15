# Public product precision repair — terminal research result

The unchanged public source is revision
`4b2ec52fc55da796aa8f5ef851290297e8706424`. The gate-inert observer reproduces
its final stream SHA256
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.

The preserved random 262,144-input census completed 68,943,872 actual
production-fold formula checks. Every raw simulation matches the protected
simulator on all qubits, bits, phase and Toffolis. The final frozen circuit
has 431 value failures on these inputs. This is not a phase/garbage census.

There are 34 discarded carry events on 34 separate inputs, all final value
failures: 13 negative forward carries and 21 positive reverse carries.
Every event belongs to a different tick. No small cluster of ticks explains
most events. At most, these observed events account for 1.1704 expected
affected inputs per 9,024 shots; a precision increase is not guaranteed to
repair every event or every final failure.

The predeclared family increases precision by one bit at the top 1, 4, 8
or 16 ranked positions for every input, using a deterministic tie break.
The first member is forward tick 1. Its raw builder diagnostics cost one
additional expected/native Toffoli with unchanged peak 1,234. These are
component diagnostics, not a complete resource measurement.

The first member compiles, then whole-circuit generation rejects with exit
101 at the unchanged `square_finish::run` input-length assertion:
11,453,360 actual versus 11,453,250 required. No full candidate stream is
produced. All existing table assertions and table data are retained. No
table bypass or failed-source resource claim was made.

Post-table feasibility: 252 of the 263 original complete raw fold regions
survive uniquely byte-identical in the final stream, with empty Push/Pop
stacks at all four raw/final boundaries. Selected forward tick 1 survives
as a 5,644-operation region, raw [642092,647736), final [642114,647758).
Temporal classical liveness admits 66 sites. The selected site's measurement
scratch version is initialized locally and overwritten unconditionally before
its next external read. Its new physical quantum wires are the next payload
bit 907 and scratch 1205. The final original prefix's last touch of scratch
1205 is an unconditional R; the new region's last touch is unconditional HMR.
This gives an input- and measurement-independent zero boundary certificate.
Old/new raw streams are byte-identical outside the selected entire region.

The post-table pass checks unique complete-region equality, empty scope
snapshots, temporal scratch-bit locality, existing quantum capacity, and the
added scratch wire's unconditional resets. Nine positive/negative native
admission tests pass. Whole generation passes every inherited table check.
Three guard revisions reproduce final SHA256
`f3e1c5b96099c2848617f1ce2008c36bc2a9a6e29067a90e382bdad6e5e46d9b`.
The final frozen guarded source is in `candidate-posttable-top1`.

An independent fresh paired census used label
`public4b-precision-top1-posttable-fresh-20261016-v1`, batches 0 through 4095,
262,144 inputs per circuit, and the unchanged protected census checker.

| Result | Public parent | One-bit candidate |
|---|---:|---:|
| Value failures | 443 | 443 |
| Phase failures | 321 | 327 |
| Dirty quantum scratch | 0 | 0 |
| Failed batches | 501 | 517 |
| Expected failed batches / 9,024 shots | 17.24634 | 17.79712 |
| Mean executed Toffoli diagnostic | 761222.84604 | 761224.07333 |

The value-failure sets are identical on every batch. Total failure membership
changes by 47 newly passing and 60 newly failing inputs, reflecting phase
changes after the extra HMR shifts subsequent random draws. The observed
paired mean Toffoli difference is +1.22729 with standard error 1.59051;
the raw source builder's expected/native increment is exactly one Toffoli.
These are complete research censuses, not an official scored passing result.

This candidate does not show a failure-rate improvement and its measured
failed-batch rate exceeds its parent. It is not eligible for nonce search
under the project's relative failure-rate standard. It is preserved as a
successful source-bound post-table construction with a negative performance
outcome. No search or submission was attempted.

The predeclared 16-site raw-component extension is also negative: later
changes escape the proposed fold regions, and incoming classical reads
persist beyond their shared prefixes. Extending regions through outgoing
scratch lifetimes admits no additional sites; some lifetimes span millions
of operations. No broader candidate was admitted or built.

All inputs, formula checks, timing, source patches and rejected generation
logs are preserved under this experiment. No nonce search, submission,
commit or push was performed.
