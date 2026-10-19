import difflib,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1]
block='''## 19 October,20:56: disabled-filter build and gated continuation prepared

Research/native proof checkpoint2d15b9d8 is pushed. The same single classical9
gate remains running, manager1377879; never restart or relabel it. No gate
verdict, new-source nonce screen, official benchmark or new resource record.

The source-bound disabled validation-tool build1401460 has exited0 in
product-classical-nine-filter-20261019. Its23 source/build archive members are
verified locally; binary SHA2561be42a4d497e172dea7a65ec58f9a3d5cfdf5b06a93c9a2bf5ec54a261db6182.
Waiting manager1401461 remains recorded. The waiter launches the existing two-thread qualification suite
only after both this build and the final new-source gate pass. Rejection and
nonce selection remain disabled. Own-source seed, full9024 state/phase/physical
RNG, zero-MR128+partial and six4096-row/timing controls are required. If the
gate fails, this watcher records NO_RUNTIME_QUALIFICATION and runs no nonce.

Its first build admission used the older registry, which did not recognize its
own idle waiter. It correctly refused at64 reserved slots before creating the
tool or testing any nonce. Verify/preserve/stop only waiting1397605; old build
1397604 and all scripts/logs/preflight are saved under failed-admission-v1.
The repaired build uses preflight_v9, which registers the exact waiter at zero
slots. Its admission passes at64 slots with no unknown research processes.
No gate, candidate, old search or old finalizer was changed by this repair.

Use latest preflight_v9.py. Build uses1 slot; qualification later uses3 slots
after the gate's3 slots end. Old search reserves60. Waiting managers reserve0.
The waiting Python/shell sources are bound in WATCH_SOURCE.json: do not edit
them while live. Inspect build.exit, qualification.exit, RESULT.json and
WATCH_RESULT.json. No operational search, old-search termination, benchmark
or uploader is enabled by this continuation. Accept/port a new operational
tool only after all new-source checks and fresh cost estimates pass.

[Disabled qualification setup](../experiments/product-classical-nine-filter-20261019/STATUS.md).

'''
patch=[]
for name in ['docs/AGENT_HANDOFF.md','docs/research-plan.md','docs/results-status.md']:
    old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode('utf-8');h,t=old.split('\n',1);new=h+'\n\n'+block+t.lstrip('\n')
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    p=root/name;h,t=p.read_text(encoding='utf-8').split('\n',1);p.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n')
(r/'checkpoint-filter-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with (r/'LOG.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n'+block.rstrip()+'\n')
p=root/'experiments/product-classical-nine-filter-20261019/STATUS.md'
with p.open('a',newline='\n') as f:f.write('\n## Recorded continuation\n\n'+block.split('\n\n',1)[1])
for p in p.parent.rglob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
print('Prepared additive filter handoff and checked all local Python syntax.')
