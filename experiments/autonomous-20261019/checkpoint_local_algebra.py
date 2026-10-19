import difflib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1];e=root/'experiments'
for name in ['product-classical-closure-20261019','product-classical-cap11-20261019']:
    assert json.loads((e/name/'LOCAL-VERIFICATION.json').read_text())['status']=='FINISHED_ARCHIVE_AND_ALL_MEMBERS_VERIFIED'
assert '9 passed; 0 failed' in (e/'product-anf256-20261019/tests.log').read_text()
block='''## 19 October,23:13: local algebra controls finished; larger sparse scan live

Qualified classical9 production remains unchanged and live. At23:12 its
four workers reported4079616 completed-window rows, no pass, about2646/s.
Counters remain provisional; the complete terminal audit is still required.
Search shell1703053 and queue-only finalizer1697009 remain the active path.
Classical12's single262144-batch final gate is still running, manager1704998,
parent child1705372; no verdict or new-source nonce. Keep both jobs unchanged.
No new scored record. See the previous qualified-cycle entry for every gate
statistic, frozen stream/source, acceptance and finalizer binding.

Independent local Ubuntu execution now works without consuming server slots:
read-only existing compiler/release dependencies,115 member hashes verified,
archive SHA256b166ab58d683971f955ca0ace7cb44da459eceebd8ae2516e2b32eb578b97129.
Large runtime/input/executable files are ignored, retained locally with hashes;
no package installed and no server compiler or chemistry/QOB job changed.

Two local source experiments finished, both negative. Reapplying the tested
cap9 factor pass to frozen classical12 gives identical complete raw2ef31475…
in44.41s. A new2048-row/eleven-atom exact table port passes all7 primitive
and exhaustive controls, reproduces the entire cap9 stream, then returns the
same complete raw stream at cap11 (136.68s, peak RSS1990564KiB). It produces
no new candidate or executed saving. Completed archives and all members are
verified: cap11 archiveb8fd70d5…/83 files. Two pre-compiler admission failures
(runtime verification not finished; ambiguous sha3 0.10/0.11) are preserved,
including every original source hash. Launcher now requires verification;
the explicit sha3-0.10.9 dependency matches the original research package.

A different fixed source screen is running locally: product-anf256-20261019,
WSL manager459/Python461/worker500 at23:12. Nine controls pass, including
8192 exhaustive13-variable polynomial assignments and whole-result degree
fallback. Fixed256 terms/degree12, one case on frozen classical12, input
compressed17c767f5…/raw2ef31475…, one local core/12GiB cap, nohup/PID/exit
and full source/command hashes. No gate, nonce or score. Inspect the same
run.exit/RESULT.json and actual process; do not restart on an observation
timeout. Any changed output requires512 complete raw state/phase/RNG controls
and later universal/native qualification; static site counts are not records.
Do not launch another local compute job until this one ends. Server capacity
remains60 search+3 census+1 spare; bound preflight_v13 and watched source are
immutable. New server job types require a reviewed registry/finalizer plan;
use local research meanwhile. Preserve all failed and Q692 evidence.

'''
patch=[]
for name in ['docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md']:
    old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();h,t=old.split('\n',1);new=h+'\n\n'+block+t.lstrip('\n')
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    p=root/name;h,t=p.read_text(encoding='utf-8').split('\n',1);p.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n')
(r/'checkpoint-local-algebra-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with (r/'LOG.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n'+block.rstrip()+'\n')
print('Prepared local algebra and live-job continuation checkpoint')
