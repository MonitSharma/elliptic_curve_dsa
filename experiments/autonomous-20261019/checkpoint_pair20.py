"""Preserve a finished negative and the next source screen's completed controls."""
import difflib,hashlib,io,json,os,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;root=r.parents[1];e=root/'experiments';p=e/'product-pair-witness-20261020'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert '22 passed; 0 failed' in (p/'tests.log').read_text()
assert json.loads((e/'product-copy-cache-witness-20261020/LOCAL-VERIFICATION.json').read_text())['status']=='FINISHED_ARCHIVE_AND_ALL_MEMBERS_VERIFIED'
files={};data={}
for q in sorted(p.iterdir()):
 if q.is_file() and (q.suffix in ['.rs','.py','.sh','.md'] or q.name in ['PREPARATION.json','LAUNCH.json','SOURCE.sha256','tests.log','build-tests.log','build.log','build-trace.log']):
  raw=q.read_bytes();data[q.name]=raw;files[q.name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Frozen exact pair-witness source, completed22 tests and builds. Full disabled/paired source screens pending. No native candidate, gate, nonce or score.',
 'included_files':files,'binary_hashes_retained_locally':{name:sha(p/name) for name in ['anf.bin','trace.bin','tests.bin']},'input_compressed_sha256':'53bb99238f013b7308b88e26d063d6d9ec3b364d1f0e2b2501b6abe368a75fb1'}
with tarfile.open(p/'controls-source.tar.gz','x:gz') as a:
 for key,raw in data.items():m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
 raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
with tarfile.open(p/'controls-source.tar.gz') as a:
 for key,v in files.items():raw=a.extractfile(key).read();assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256']
(p/'CONTROLS-SOURCE.json').write_text(json.dumps({'status':'COMPLETED_CONTROLS_AND_FROZEN_SOURCE_ARCHIVE_VERIFIED_FULL_SCAN_PENDING','sha256':sha(p/'controls-source.tar.gz'),'files':len(files),'binary_sha256':manifest['binary_hashes_retained_locally']},indent=2)+'\n')
block='''## 20 October,01:13: first cache follow-up negative; exact XOR-pair controls pass

No new scored record. Source12 production/finalizer and the sole cache census
continue unchanged. At01:12 source12 reported1421312 completed-window rows,
no pass, about2554/s; only a complete terminal audit certifies nonce coverage.
The previous01:07 entry contains every actual PID/source/gate/runtime binding.
Checkpoint ad638dc9 is pushed. The initial combined commit/push approval was
refused; read-only verification found the explicit origin-main push instruction
in the user-referenced AUTONOMOUS_PROMPT.md and confirmed matching remote HEAD,
repository destination and no staged workflows/user edits. Reversible commit
and authorized fast-forward push then passed review. No blocked publication.

product-copy-cache-witness-20261020 finished0: unchanged tested interpreter,
16 controls, fixed cache input raw d343ca71…, full output identical,0 sites.
Completed archive and every member verified. No additional saving or candidate;
do not repeat this exact new-input screen. All old negative/failed evidence stays.

New LOCAL product-pair-witness-20261020 is live, WSL shell442/Python444,
one core/12GiB. All22 primitive/exhaustive/index/corruption controls PASS.
The new method proves P=wireU XOR wireV, optionally complemented, by a live
monomial inverse index and pure symmetric difference. Every valid pair must
contain the chosen nonconstant product term in exactly one member; enumeration
uses that term's complete current-wire set. Queries allocate no abstraction
atoms or cuts, exclude target/controls, keep original classical guards and add
no R/Hmr/q. CCX becomes two CX plus optional X. This is a source hypothesis.
Whole-source disabled-mode report/hash reproduction is currently running;
enabled fixed cap256/degree12 scan follows only if it passes, then512 raw
q/c/phase/physical-RNG controls if changed. Frozen source/22 tests/build logs
and binary hashes are sealed in controls-source.tar.gz, every member verified.
No native proposal, statistical gate, source-specific nonce or scored count.
Do not edit/relaunch the running source; use existing RESULT/run.exit/PID.

'''
patch=[]
for name in ['docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md']:
 old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();h,t=old.split('\n',1);new=h+'\n\n'+block+t.lstrip('\n')
 patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
 q=root/name;current=q.read_text(encoding='utf-8');h,t=current.split('\n',1);pending=q.with_name(q.name+'.next-checkpoint')
 pending.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n');os.replace(pending,q)
(r/'checkpoint-pair20-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with (r/'LOG.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n'+block.rstrip()+'\n')
print('Sealed22 controls and exact pair source; prepared actual negative/new-screen checkpoint')
