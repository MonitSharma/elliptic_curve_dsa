"""Preserve current nonignored workspace and nested edits for authorized push."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,json,hashlib,re
root=Path(__file__).resolve().parents[2];r=root/'experiments/github-snapshot-20261021';r.mkdir(exist_ok=False)
def g(*args,cwd=root):return subprocess.check_output(['git','-C',str(cwd),*args])
assert not g('diff','--cached','--name-only').strip()
sha=lambda b:hashlib.sha256(b).hexdigest();manifest={}
(r/'.gitattributes').write_bytes(b'* -text\n')
for name in ['qubits','toffoli','product']:
 track=root/'agents'/name;d=r/'nested'/name;d.mkdir(parents=True)
 patch=g('diff','--binary','HEAD',cwd=track);(d/'tracked-changes.patch').write_bytes(patch)
 names=g('diff','--name-only','HEAD','-z',cwd=track).decode().split('\0')
 untracked=g('ls-files','--others','--exclude-standard','-z',cwd=track).decode().split('\0')
 files={}
 for n in sorted(set(names+untracked)-{''}):
  p=track/n;assert p.is_file()and p.stat().st_size<100_000_000,n
  dest=d/'working-files'/n;dest.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes();dest.write_bytes(raw);files[n]={'sha256':sha(raw),'kind':'untracked'if n in untracked else'tracked_modified'}
 manifest[name]={'base_commit':g('rev-parse','HEAD',cwd=track).decode().strip(),'status':g('status','--short',cwd=track).decode(),'patch_sha256':sha(patch),'files':files,'restore':'Use the recorded base commit; apply tracked-changes.patch and copy untracked files from working-files preserving relative paths. Check before applying over edits.'}
(r/'NESTED-WORKTREE-SNAPSHOT.json').write_text(json.dumps(manifest,indent=2)+'\n')
(r/'README.md').write_text('''# GitHub snapshot — 21 October 2026

The human explicitly requested pushing everything after the research break.
All current nonignored root files are included. The challenge tracks point to
the upstream Layr-Labs repository; their uncommitted edits are preserved here
as binary-capable patches plus exact current source files and SHA256 manifests.
The submodule checkouts themselves are left intact, and their existing base
commits remain available. No challenge submission or research job was resumed.

Generated ignored build trees, environments and operation-stream caches remain
local. Qualified source archives, evidence and disclosed experimental logs are
included in the repository. See docs/RESEARCH_BREAK_2026-10-21.md for the current
paused state and safe future resume instructions.
''')
p=root/'docs/RESEARCH_BREAK_2026-10-21.md';s=p.read_text();needle='Only root commit `41f769ec44e40c915c3149d8332c15b10bca71f8` was explicitly\napproved and pushed previously. That approval is already fulfilled. Newer\ncommits remain local; do not treat it as permission to push a later HEAD.'
assert needle in s;s=s.replace(needle,'The human subsequently instructed **“Push everything to github”** on21October2026.\nThat authorizes syncing all current saved commits and remaining nonignored root\nfiles. Nested challenge edits are preserved as patches and exact source snapshots\nin `experiments/github-snapshot-20261021/`; upstream challenge branches are unchanged.\nResearch remains paused. The earlier commit-specific41f769ec approval is historical.');p.write_text(s)
p=root/'experiments/autorun-20261020-breakthrough/CURRENT-ACTIVE.json';d=json.loads(p.read_bytes());d['push_status']='USER_EXPLICITLY_AUTHORIZED_PUSH_EVERYTHING_ON_2026-10-21; sync current root commits/files and nested source snapshots to origin/main; verify remote HEAD after push. Research remains PAUSED.';d['github_snapshot']='experiments/github-snapshot-20261021/NESTED-WORKTREE-SNAPSHOT.json';p.write_text(json.dumps(d,indent=2)+'\n')
with(root/'experiments/autorun-20261020-breakthrough/LOG.md').open('a',encoding='utf-8')as out:out.write('\n## '+datetime.now(timezone.utc).isoformat()+' — GitHub sync authorized\nHuman explicitly requested pushing everything. Preserve all remaining nonignored rootfiles and all nested tracked/untracked edits as exact source snapshots/patches; no upstream challenge modification. Existing20localcommits plus new workspace checkpoint authorized for origin/main. Research remains PAUSED; no workload/nonce/submission resumed.\n')
paths=set(g('ls-files','--others','--exclude-standard','-z').decode().split('\0'))|set(g('diff','--name-only','-z').decode().split('\0'));paths.discard('');paths={p for p in paths if not p.startswith('agents/')}
for name,track in manifest.items():
 paths.update((r/'nested'/name/'working-files'/n).relative_to(root).as_posix()for n in track['files'])
secret=re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|sk-proj-[A-Za-z0-9_-]{40,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
findings=[];sizes={}
for n in sorted(paths):
 p=root/n
 if not p.is_file():continue
 size=p.stat().st_size;assert size<100_000_000,(n,size);sizes[n]=size
 if p.suffix not in ['.gz','.png','.jpg','.zip','.pdf']:
  if secret.search(p.read_bytes()):findings.append(n)
assert not findings,('Potential credential material; do not publish',findings)
receipt={'at_utc':datetime.now(timezone.utc).isoformat(),'status':'CURRENT_WORKSPACE_REVIEWED_READY_FOR_AUTHORIZED_GITHUB_SYNC','root_before_commit':g('rev-parse','HEAD').decode().strip(),'root_paths':len(paths),'root_file_bytes':sum(sizes.values()),'nested_tracks':manifest,'files_over_github_100MB_limit':0,'credential_pattern_findings':0,'research_status':'PAUSED_NO_JOBS_RESUMED','note':'Standard ignored generated/build/environment files excluded. No upstream submodule push. Remote main must be verified after push.'}
rp=r/'SYNC-PREPARATION.json';rp.write_text(json.dumps(receipt,indent=2)+'\n');paths.add(rp.relative_to(root).as_posix())
subprocess.run(['git','-C',str(root),'add','-f','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(p.encode()for p in sorted(paths))+b'\0',check=True)
staged=set(g('diff','--cached','--name-only').decode().splitlines());assert staged<=paths;assert not any(p.startswith('agents/')for p in staged)
subprocess.run(['git','-C',str(root),'diff','--cached','--check','--','docs/RESEARCH_BREAK_2026-10-21.md'],check=True)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve remaining workspace and nested research edits for GitHub sync'],check=True)
print(g('rev-parse','HEAD').decode().strip());print('Committed',len(staged),'root paths, with nested patches and exact source snapshots. Research remains paused.')
