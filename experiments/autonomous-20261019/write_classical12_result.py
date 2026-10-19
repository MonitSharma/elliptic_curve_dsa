"""Document only the independently verified complete benchmark, preserving user edits."""
import difflib,json,os,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1];e=root/'experiments';p=e/'classical12-final-20261020'
read=lambda p:json.loads(Path(p).read_text());local=read(p/'LOCAL-FINAL-VERIFICATION.json');a=local['metrics'];bench=read(p/'BENCHMARK_RESULT.json');gate=read(p/'evidence/gate/RESULT.json');native=read(p/'NATIVE_RECEIPT.json');source=read(p/'SOURCE_FREEZE.json')
assert local['status']=='COMPLETE_FINAL_ARCHIVE_ALL_MEMBERS_AND_SELECTED_SOURCE_VERIFIED_LOCALLY' and a['product_improvement']>0
when=datetime.now(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
block=f'''## {when}: complete lower-product benchmark verified and queued

UNCHANGED native benchmark PASS at Q{a['qubits']}, rounded mean executed
Toffolis{a['rounded_mean_executed_toffoli']}, complete product{a['product']}.
Total T{bench['total_executed_toffoli']} across9024 shots, mean
{bench['mean_executed_toffoli']:.12f}; zero classical mismatches, phase-garbage
batches and dirty-ancilla batches. Independently refreshed public parent
9dc3798c remains Q1234/T761096/product{a['public_product']}; local complete
improvement{a['product_improvement']} ({100*a['product_improvement']/a['public_product']:.8f}%).
This is a complete LOCAL benchmark reproduction, not an official upload or
publicly promoted record. Queue mode: no uploader invoked.

Lowest protected passing nonce7614812. Every7,811,072 terminal production row
was audited, all workers exited0, complete lower prefix covers the nonce;
196260 parallel-overrun rows are disclosed. Preliminary28950 repeated row
attempts over unique1..4096 and own-seed/full-state references are separate.
Only the inherited identity tail nonce changes on the frozen source12 circuit;
no score-based nonce choice or packet/content/table/cut tuning. Exact native
pre-tail bytes and48 XX pairs verified;512 existing-gate-row tail controls PASS.

The sole predeclared classical12 gate remains PASS, label
{gate['label']},262144x64 per source. Candidate/parent value shots28574/28574,
failed batches33148/33203, dirty0; b2912,c2967, exact McNemar p
{gate['mcnemar_one_sided_p']}, candidate failed batches/9024 packet
{gate['failed_batches_per_packet']['candidate']}. Complete phase/failing-shot
rates are in DISCLOSED-CENSUS-COUNTS.json, derived only from existing rows.
All earlier failure verdicts, including Product25, stay final and ineligible.

Selected stream{native['candidate_stream_sha256']}; source archive
{source['selected_source_archive_sha256']}. All180 source/protected17 files
verified; changes confined to src/point_add. All relevant18 native primitive
tests pass, own-source runtime/seed/cost/prefix checks pass, complete nonce
audit is bound, unchanged harness/scorer/Cargo/toolchain and historical
results.tsv are preserved. Final full evidence archive and every member,
including selected source archive, pass local verification.

Review: experiments/classical12-final-20261020/SUBMISSION-NOTE.md,
QUEUED-READY.json, LOCAL-FINAL-VERIFICATION.json, final-evidence.tar.gz and
evidence/. The source/patch/logs/census hashes/search accounting are ready for
review. Full terminal JSONLs and generated streams remain server-retained,
independently rehashed; original full gate archive is already preserved here.
The live watched source/profile files were not edited during finalization.

Independent further work stays separate: the extra copy-cache source's sole
gate FAILED (McNemar p0.017701059294805803) and is permanently ineligible.
Its runtime waiter refused before any own-source nonce evaluation. No rerun,
relabel, larger census or nonce search; its full failed archive is preserved.
The sparse linear scan finished0 with30 controls and complete baseline control,
0 sites and unchanged raw output. Width footprint/clean-boundary/first-peak
rank studies are also preserved; exact conservative rank1233 certifies no
free parity donor at the fixed first peak, not physical-width optimality.
None of those component/diagnostic counts is a record or result-plot point.
Preserve all old verdicts, Q692 and pre-existing user edits.

'''
readme=f'''## New local benchmark · {when}

The complete unchanged benchmark passes at **{a['qubits']:,} qubits ×
{a['rounded_mean_executed_toffoli']:,} rounded mean executed Toffolis =
{a['product']:,}**, improving the freshly verified public product by
**{a['product_improvement']:,} ({100*a['product_improvement']/a['public_product']:.5f}%)**.
All 9,024 shots pass. This is a **local reproduction, queued for review**;
it has not been uploaded or officially evaluated. The frozen circuit passed
its independent failure-rate gate; lowest passing nonce 7,614,812 after full
accounting of 7,811,072 production nonces. Inherited approximate arithmetic
remains, so finite-packet success is not a universal correctness claim.

[Source, statistical census and complete nonce accounting](experiments/classical12-final-20261020/SUBMISSION-NOTE.md) ·
[Independent local verification](experiments/classical12-final-20261020/LOCAL-FINAL-VERIFICATION.json) ·
[Complete evidence bundle](experiments/classical12-final-20261020/final-evidence.tar.gz)

'''
patch=[]
for name,addition in [('README.md',readme),('docs/research-plan.md',block),('docs/AGENT_HANDOFF.md',block),('docs/results-status.md',block)]:
 old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();h,t=old.split('\n',1);new=h+'\n\n'+addition+t.lstrip('\n')
 patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
 path=root/name;current=path.read_text(encoding='utf-8');assert addition.splitlines()[0] not in current,'Never duplicate an existing final result'
 backup=r/'final-user-working-backups';backup.mkdir(exist_ok=True);(backup/'.gitignore').write_text('*\n!.gitignore\n');dest=backup/path.name;assert not dest.exists();dest.write_bytes(path.read_bytes())
 h,t=current.split('\n',1);pending=path.with_name(path.name+'.next-checkpoint');pending.write_text(h+'\n\n'+addition+t.lstrip('\n'),encoding='utf-8',newline='\n');os.replace(pending,path)
(r/'classical12-final-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with (r/'LOG.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n'+block.rstrip()+'\n')
ready=e/'autorun-20261020-classical12-ready';ready.mkdir(exist_ok=False)
(ready/'READY.md').write_text('# Queued complete local product improvement\n\n'+block+'\nSubmission mode:queue. No official uploader invoked.\n',encoding='utf-8',newline='\n')
print('Prepared verified complete local result, submission queue and additive docs/README patch')
