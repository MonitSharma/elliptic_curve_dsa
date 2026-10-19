"""Preserve the verified controls and exact serial research queue."""
import difflib,hashlib,io,json,os,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;root=r.parents[1];e=root/'experiments';p=e/'product-linear-witness-20261020'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
native=json.loads((e/'product-linear-witness-controls-v2-20261020/LOCAL-VERIFICATION.json').read_text());assert native['tests']==30 and native['files']==43
pair=e/'product-pair-witness-20261020';disabled=json.loads((pair/'disabled.json').read_text());baseline=json.loads((e/'product-copy-cache-witness-20261020/RESULT.json').read_text())['source']
assert disabled==baseline and 'Exit status: 0' in (pair/'disabled.log').read_text()
bound=json.loads((p/'WATCH_SOURCE.json').read_text());assert all(sha(p/name)==h for name,h in bound.items())
files={};data={}
for q in sorted(p.iterdir()):
 if q.is_file() and (q.suffix in ['.rs','.py','.sh','.md'] or q.name in ['PREPARATION.json','WATCH_SOURCE.json','watch.pid']):
  raw=q.read_bytes();data[q.name]=raw;files[q.name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Frozen local sparse linear prototype and idle serial waiter; exact source already passes30 server primitive controls. No local whole-source scan yet. No circuit/gate/nonce/score.', 'included_files':files,'native_control_archive_sha256':native['sha256']}
with tarfile.open(p/'queued-source.tar.gz','x:gz') as a:
 for key,raw in data.items():m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
 raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
with tarfile.open(p/'queued-source.tar.gz') as a:
 for key,v in files.items():raw=a.extractfile(key).read();assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256']
(p/'QUEUED-SOURCE.json').write_text(json.dumps({'status':'ALL_FROZEN_QUEUE_SOURCE_MEMBERS_VERIFIED','sha256':sha(p/'queued-source.tar.gz'),'files':len(files),'native_primitive_tests':30,'whole_source_result_pending':True},indent=2)+'\n')
block='''## 20 October,01:29: XOR-pair baseline passes; sparse linear controls and queue ready

No new scored record. Source12 search/finalizer remain unchanged. At01:29,
4317184 completed-window rows reported, no pass,2780/s; live counters are
provisional. Copy-cache's original parent262144-row census half is complete;
its candidate half is LIVE under2137416, manager2037609/shell2037534.
No verdict yet. Existing runtime waiter2074877 still waits for the sole own
gate PASS and actual gate/build manager exit. Never restart or relabel it.

Local XOR-pair source screen's entire disabled-mode report and raw stream
reproduce the previous complete cache-witness result exactly.11m49.46s,
peak RSS2174432KiB. All22 tests remain passing. Enabled fixed source scan
is now live in the same shell442/Python444, time584 at01:24; at01:29 it had
passed8m operations with0 sites so far. Final RESULT/exit is authoritative;
partial diagnostic counters are never scored counts. No new native source,
census, nonce or score. Exact raw input d343ca71…/17889637 operations.

New product-linear-witness-20261020 has30 primitive/exhaustive controls PASS
on the spare server slot. Every sparse GF2 row carries current physical-wire
provenance and a constant. A write invalidates ALL rows using that wire,
including swaps/reset/measurement. Fixed1024-term/32-wire limits drop proof
opportunities safely; missing/oversize reductions never mean zero. Queries
allocate no abstraction atoms/cuts, exclude target/original controls, retain
classical guards, and emit only CNOTs plus optional X. This is a bounded valid
span, not a completeness claim for every current-wire relation. No new width,
R/Hmr or phase event. Eight new controls include exhaustive small-polynomial
row/provenance mutations, bounds, guarded three-wire products, complements,
dirty-target exclusion and full protected arbitrary-basis/phase comparisons.

Initial server admission2114797 exited1 BEFORE any compiler/tests: the global
load guard inherited a one-CPU affinity because pinning occurred first. Old
source/descriptor/log are untouched. New namespace v2 moved the unchanged
global capacity check before pinning actual work;2117989 exited0,30/30 PASS.
Same Rust sources/compiler/dependencies. Full43-member archive1e46f5ba…
and exact local prototype source match are locally verified. No circuit,
statistical gate or nonce was evaluated by either primitive-control job.

Idle LOCAL waiter580 in product-linear-witness-20261020 is live and hashes
all source/driver files. Only after the existing pair screen exits0 will it
launch the one serial full-source linear screen. Local source and source-bound
native-control hashes rechecked, then30 tests, whole pair-baseline report/hash
reproduction, enabled fixed scan and512 complete raw q/c/phase/RNG controls
if changed. One local CPU/12GiB; no concurrent local compute, rerun or live
source edit. Verified queued-source archive preserves every frozen member.

A different product direction is written in product-parity-lease-plan-20261020:
temporary compression of an idle held ancilla around a highest-wire epoch,
then exact restoration. This differs from the completed negative whole-cache
removal study. AtQ1233 the current record permits rounded mean<=761713,
617T above the public parent. Plan only, no implementation/job/width result.
Whole-program Q/T, all boundary/phase/RNG proofs, new native source/own single
gate/runtime/lowest-nonce/unchanged benchmark are mandatory for any positive.

Keep source12 production and the cache candidate census undisturbed. Inspect
the one pair scan when terminal, then the serial linear screen. No component
or source count is a record, old failure verdicts/Q692 remain preserved, and
chemistry jobs and pre-existing user edits remain untouched.

'''
patch=[]
for name in ['docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md']:
 old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();h,t=old.split('\n',1);new=h+'\n\n'+block+t.lstrip('\n')
 patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
 q=root/name;current=q.read_text(encoding='utf-8');h,t=current.split('\n',1);pending=q.with_name(q.name+'.next-checkpoint')
 pending.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n');os.replace(pending,q)
(r/'checkpoint-linear20-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with (r/'LOG.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n'+block.rstrip()+'\n')
print('Sealed exact sparse linear queue, verified30 controls and recorded live candidate census phase')
