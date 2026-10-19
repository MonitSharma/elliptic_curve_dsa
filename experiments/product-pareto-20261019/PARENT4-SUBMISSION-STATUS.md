# Small product candidate — submission authorized, not yet submitted

## 19 October,16:14: complete proof and filter passed; ascending search active

See [current checkpoint](../product-parent-sat-20261019/CHECKPOINT-1609.md). Search PID602346 and automatic final-verification watcher PID610395 are active. Historical checkpoints below retain their original timing and outcomes; the84-stage candidate subsequently failed its single gate and is ineligible. No new benchmark result yet.

## Checkpoint: 19 October, 11:39 Singapore

The64GiB transfer-proof attempt finished with exit101. It still could not
establish equality at the public parent's second retained product, operation
14247262. This is an inconclusive proof, not a concrete circuit counterexample.
The passing statistical gate is unchanged. No nonce search or submission has
started; the fast-filter transfer remains unqualified.

The separate84-stage optimization is still running under detached PID443914.
Stages1–33 have been generated and the generation log reports their audits
passing; stage34 is generating. No complete new benchmark result yet.

On 19 October 2026 the user authorized submitting this candidate with model
attribution **GPT-6 Astra**. The work is being performed in Codex. No further
submission permission is needed once all existing eligibility checks pass.

The single predeclared final failure-rate gate **passed**. Label:
`pareto-parent4-gate-20261019-v1`, 32,768 batches of 64 shots per circuit
(2,097,152 shots each). Exact public parent: `9dc3798c-93e0-4da4-a6a9-37586737c4af`.

| Measurement | Public parent | Small candidate |
|---|---:|---:|
| Wrong-output shots | 3,619 | 3,619 |
| Failed batches | 4,171 | 4,149 |
| Failed batches per 9,024-shot packet | 17.947723 | 17.853058 |
| Dirty-ancilla shots | 0 | 0 |
| Diagnostic mean executed Toffolis | 761,093.954603 | 761,089.205897 |

Newly failing/passing paired batches: 350/372. One-sided exact McNemar
p = 0.8039858338. Paired saving = 4.748705 ± 0.574923 T (standard error).
Width remains 1,234. These are census diagnostics, **not a benchmark record**.
The verdict is final; never rerun it to change the outcome.

Frozen native stream SHA-256:
`9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a`.
The full source manifest, protected-file hashes, declaration and result are
in `parent4-qualification/`; complete rows, source archive and logs are also
preserved in that directory on the server.

Remaining work: qualify a sound candidate-bound fast filter, perform ascending
nonce screening from 1 and choose the lowest passing nonce, reproduce the
unchanged pre-tail circuit, pass the unchanged official benchmark, and refresh
the public product record before upload. Do not choose a later nonce by its
Toffoli score if the first passing nonce does not beat the record.

The public parent adds 27 retained products and one zero-row removal to the
previously certified 67-stage circuit. Independent checks of these exact
transformations are required before reusing that circuit's value filter.
The proof jobs are separate from the passing statistical gate; they never
change the candidate or repeat that gate.

Proof attempts are preserved:

- `parent4-transfer`: expression cap8192 reached its32GiB memory cap. Its
  genuine exit134 is in `parent4-transfer/parent4-transfer.exit` because that
  first wrapper used a relative marker after changing directories.
- `parent4-transfer-v2` launcher initially failed before running a proof because
  it looked for that marker in the root. The launcher log/exit1 are retained.
- `run-parent4-transfer-v3.sh` uses absolute markers and a1024-term expression
  cap. It stopped with exit101 at the second product equality, operation14247262.
  This is an inconclusive symbolic proof, not a measured counterexample.
- `run-parent4-transfer-local.sh` adds an existing exact local equality proof
  with arbitrary values at the interval boundary. Global checking still proves
  clean untouched donors and unconditional endpoints. It runs two mutation
  tests before checking the public parent. Current proof directory:
  `parent4-transfer-local/`.
- `run-parent4-filter-qualification-v2.sh` waits for that proof's genuine exit0,
  then builds a candidate-bound copy of the existing filter and validates it
  against protected simulator controls. Authoritative rejection remains
  disabled. It stops automatically on a failed prerequisite.

No operational nonce search, benchmark or upload is queued by these scripts.
After a successful filter qualification, bind and validate the operational
search before launching it. User submission authorization remains in force.

At11:01 Singapore, the arbitrary-cut and globally seeded local checks both
stopped at the same second equality. Their mutation tests passed (2 and3,
respectively); neither established the needed transfer theorem. The dependent
filter-qualification jobs correctly stopped, with no filter/search enabled.
This does not overturn the passing statistical gate or constitute a concrete
counterexample to the circuit. A final bounded proof attempt
`run-parent4-transfer64.sh` retries the original8192-term verifier with64GiB
address space after checking more than200GiB is available. Its PID/log/exit
prefix is `parent4-transfer64`; its output is in `parent4-transfer64/`.
The detached retry PID is465441. The11:02 evidence snapshot contains106 files
(including all final census rows), with SHA256
`9c9b8ed34ed248e732f45094782813d83a591b70148c73528505bbb6068c2665`;
archive `parent4-evidence-20261019T030212Z.tar.gz` is saved locally and remotely.

## Server persistence

The main 84-stage run is PID **443914**, session/group **443914**, parent PID 1.
It was launched with `setsid nohup`, stdin `/dev/null`, and stdout/stderr in
`continuation84.nohup.log`. It survives an SSH disconnect and does not require
the user's computer to remain connected. As checked at11:01 Singapore it had
generated16 of84 fixed stages. Its exit marker appears only on actual exit.

Reconnect and check:

```bash
ssh smu_server
cd /home/hclau/ecdsa_research/product-pareto-20261019
cat continuation84/PROGRESS.json
tail -20 continuation84-generation.log
cat continuation84.exit 2>/dev/null
```
