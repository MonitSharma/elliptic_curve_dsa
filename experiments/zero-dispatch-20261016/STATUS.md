# Direct dispatch: exact component comparison

The isolated direct-threaded evaluator matches every quantum/classical word of
the pinned original zero-MR evaluator on 8,192 arbitrary lanes and 512 actual
fixture inputs. Empty programs, malformed opcodes, scope underflow, capacity
overflow and unclosed scopes return the same statuses. Each timed repetition
also checks complete output equality. No production source or library changed.

Twenty-one alternating trials give median times per 512-input evaluation:
35.279 ms original, 34.902 ms with lazy guard loads, and 28.423 ms with direct
dispatch. The latter is 19.4% less time for this component, approximately1.24x
throughput. This is a runtime measurement, not a Toffoli or product result.
Full-pipeline impact is being measured separately with rejection disabled.

The compact operation stream is unchanged at SHA256
`812f706d2edd7e821ff6c5f72db5e7e65b3f9756f562d99c1d0e1fceb007daf0`.
Original library SHA256:
`84b73bcdee01bb537d0320f9985a682758d1076860455ad382a2ae175690ea82`.
Direct-dispatch library SHA256:
`1444e146e9359940123af3b951069c768313947f601d201b4bc391d8ac45cb95`.
Only dispatch and when the same guard expression is loaded change; all opcode
bodies, indices, scope semantics and zero-MR assignments are preserved.
The source generator and all three C files are retained.

An initial availability probe found no NumPy in server Python; the benchmark
therefore uses the standard library only. No package or external environment
was changed. The actual calculation used one core and a dedicated nohup log.
There was no nonce search, nonce selection or active-runtime replacement.
