from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=a.parent;r=ex/'research-break-20261021'
def git(*args):return subprocess.check_output(['git','-C',str(root),*args])
assert not git('diff','--cached','--name-only').strip()
prefixes={
'README.md':'''## Research paused for a break · 21 October 2026

Paused at the user's request. **Start with the [complete next-agent handoff](docs/RESEARCH_BREAK_2026-10-21.md)**
for official results, successful and unsuccessful experiments, source/evidence
locations, paused jobs and safe resume instructions. All local experiments are
finished; the two remaining owned server jobs are suspended with state preserved.
No automatic restart. Latest official Toffoli result: **Q1464/T746089**;
global product **932057476** remains unbeaten. Q692 evidence is preserved.

''',
'docs/AGENT_HANDOFF.md':'''## Current entry point: user-requested break · 21 October 2026

**PAUSED. Do not resume or start work without a subsequent human instruction.**
Read [RESEARCH_BREAK_2026-10-21.md](RESEARCH_BREAK_2026-10-21.md) first. It supersedes
older ACTIVE/running/pending descriptions below and includes every recent trial,
official source/gate/nonce/benchmark evidence, known failures, exact paused PID
identities and the grid timeout caveat. Machine state is
`experiments/autorun-20261020-breakthrough/CURRENT-ACTIVE.json`.

Official cb2253 Q1467/T746099 then8d704a6b Q1464/T746089 reproduced;207source and
17protected bytes exact. Globalproduct932057476 remains lower. Both already
submitted; no duplicate upload or pending PR. All local runs finished. Server
search3278347/3279048 and grid3367997/3376539/3376540 are SIGSTOP-paused, not killed.
Search has173072complete rows/fullprefix173056/highest173160/no pass. Verify
start_ticks/cwd/argv before any future resume; no automatic restart. Retired6192
stays retired. Exact approved41push was completed earlier; newercommits local.

''',
'docs/research-plan.md':'''## Research paused at human request · 21 October 2026

The authoritative [break handoff](RESEARCH_BREAK_2026-10-21.md) records all current
results, failures, preserved experiments and resume instructions. No new work
until the human resumes. All local runs completed; two owned server trees are
suspended in memory. Product objective unfinished, Q692 preserved.

Important estimate correction: the old512x64 development comparison already
included114fresh context caches. CachedQ1233 mean756053.1765 is about127T above
the product allowance755926.5823, before a few new exact reductions. Do not
subtract114again. Cap11native14/full144 gives no gain. Associative-prefix
native19/full96 gives one compactQ1233 CCX-to-CX and two oldFFE native reductions;
component only, not yet a finished/gated/scored candidate. Same-target common-
control Toffoli/CCZ fusion is an unimplemented idea; no code/test/result exists.
The predeclared15-mode exact carry grid and own-gated semantic nonce search are
paused; their sources, logs and search rows are sealed and independently verified.

''',
'docs/results-status.md':'''## Latest status: PAUSED · 21 October 2026

Officially confirmed **Q1464/T746089/product1092274296**, submission8d704a6b,
all9024 unchanged benchmark shots PASS, all207published source/17protected bytes
match. Preceding cb2253 Q1467/T746099 also confirmed. Attribution GPT-6 sol/Codex.
These improve the independent Toffoli record; globalproduct932057476 remains
unbeaten and caused promotion rejection. No pending upload/PR for either result.

See [complete break handoff](RESEARCH_BREAK_2026-10-21.md) for gates, disclosed
nonces/screens and evidence. Component diagnostics are not scored results.
All local jobs completed; two owned server jobs SIGSTOP-paused on human request.
No automatic restart. Older active/queued descriptions below are historical.

''',
'docs/frontier-results.md':'''## Verified update and research break · 21 October 2026

Latest official independent Toffoli minimum is **1464×746089=1092274296**,
[submission8d704a6b](https://api.ecdsa.fail/api/submissions/8d704a6b-659c-4d67-9bd0-f6862de9f617).
The complete benchmark passes all9024 shots and public source matches all207
source/17protected files. Globalproduct remains932057476; width minimum669.
Work is paused at human request. [Full handoff](RESEARCH_BREAK_2026-10-21.md)
separates all component/proxy/failed trials from verified scores. Existing plots
and pre-existing user changes were preserved; no diagnostic points were added.

''',
'docs/AUTONOMOUS_PROMPT.md':'''# Current override: research paused at the user's request

As of21October2026, do not execute the unattended prompt below until a subsequent
human instruction resumes the task. Read [the break handoff](RESEARCH_BREAK_2026-10-21.md)
first. Two owned server jobs are SIGSTOP-paused and all local jobs finished;
resume requires fresh resource and PID/start_ticks checks. No automatic restart
or automation exists. The remaining prompt is the preserved historical workflow.

''',
'experiments/autorun-20261020-breakthrough/READY.md':'''# Current state: user-requested break, no pending upload

Read [the authoritative handoff](../../docs/RESEARCH_BREAK_2026-10-21.md).
Official cb2253 Q1467/T746099 and8d704a6b Q1464/T746089 are both complete and
confirmed. Do not upload duplicates. No new PR was created. New compact/Boolean
results are component-only and not ready for submission. Globalproduct remains
unbeaten. All local jobs finished; two server jobs suspended, no automatic resume.
Historical ready/queued entries below are retained as historical evidence.

'''}
for p,prefix in prefixes.items():
 path=root/p;old=path.read_text(encoding='utf-8')
 if not old.startswith(prefix):path.write_text(prefix+old,encoding='utf-8')
 baseline=git('show','HEAD:'+p);blob=subprocess.check_output(['git','-C',str(root),'hash-object','-w','--stdin'],input=prefix.encode()+baseline).decode().strip()
 subprocess.run(['git','-C',str(root),'update-index','--cacheinfo','100644,'+blob+','+p],check=True)
names=['research-break-20261021','breakthrough-current-compact-grid-20261021','breakthrough-public-semantic-nonce-20261021','breakthrough-compact-context-alias-20261021','breakthrough-reset-reference-inventory-20261021','breakthrough-compact-generic-repeat-20261021','breakthrough-current-cap11-20261021','breakthrough-associative-prefix-20261021','breakthrough-implicit-classical-guards-20261021','breakthrough-implicit-classical-guards-v2-20261021']
paths=['docs/RESEARCH_BREAK_2026-10-21.md']
for name in names:
 d=ex/name
 for p in d.rglob('*'):
  rel=p.relative_to(d)
  if any(x in rel.parts for x in ['candidate','observer','local-tool','target','__pycache__']):continue
  if p.name.endswith('.ops.bin')or p.name.endswith('.jsonl')or p.name in ['ops.bin','normalized-value-ir.bin.zst','final-evidence.tar.gz']:continue
  if p.is_file()and p.stat().st_size<20_000_000:paths.append(p.relative_to(root).as_posix())
helpers=['prepare-compact-context-alias.py','prepare-current-compact-grid.py','install-current-compact-grid.py','CURRENT-COMPACT-GRID-TRANSFER.json','prepare-reset-reference-inventory.py','prepare-compact-generic-repeat.py','prepare-current-cap11.py','prepare-associative-prefix.py','pause-research-for-break.py','save-break-handoff.py','finalize-break-checkpoint.py','CURRENT-ACTIVE.json','LOG.md']
paths.extend((a/p).relative_to(root).as_posix()for p in helpers)
paths=sorted(set(paths));subprocess.run(['git','-C',str(root),'add','-f','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(p.encode()for p in paths)+b'\0',check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();assert set(staged)<=set(paths)|set(prefixes)
# Explicitly exclude all user data/figures and nested submodules from this commit.
assert not any(p.startswith(('docs/data/','docs/figures/','agents/'))for p in staged)
# Evidence retains its sealed CRLF/blank lines exactly; check human-written docs.
subprocess.run(['git','-C',str(root),'diff','--cached','--check','--',*prefixes,'docs/RESEARCH_BREAK_2026-10-21.md'],check=True)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Pause ECDSA research and preserve complete results, failures and resume handoff'],check=True)
print(git('rev-parse','HEAD').decode().strip());print('Saved',len(staged),'owned paths; existing user suffix edits remain unstaged; no push.')
