"""Update only the staged checkpoint paragraph after the native job finishes."""
import difflib,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
old='''Active: breakthrough-phase-pebble-modular-20261020 supervisor2435977.
Optional carry and exact leading-zero trim/hook offsets, full plain modular
ripples and pure square chunks; copy/deferred/known-output/known-terminal/
external-carry contracts remain excluded. Original outer planners/windows/
iterations fixed. Native3+1+4+3 controls before1234/1233 generation; require
1234 exact13f6 and inspect actual peak/touched IDs before further replay.
'''
new='''Modular integration2435977 passes3+1+4+3 controls and baseline exact13f6,
but candidate1233 generation fails Y42 at forward87 after a freshID1233 is
allocated. No complete candidate or cost exists. Metadata-only storage audit
supervisor2440557 is active; original consistency assertions remain intact.
The integrated zero/live-carry source excludes copy/deferred/known-output/
known-terminal/external-carry contracts. Outer planners/windows/iterations
remain fixed. Strengthened zero-carry34-member archive also verifies locally.
'''
patch=[]
for name in['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;index=subprocess.check_output(['git','show',':'+name],cwd=root).decode();assert index.count(old)==1;updated=index.replace(old,new)
 patch.extend(difflib.unified_diff(index.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
 data=p.read_bytes();old_bytes=old.encode();new_bytes=new.encode()
 if old_bytes not in data:old_bytes=old_bytes.replace(b'\n',b'\r\n');new_bytes=new_bytes.replace(b'\n',b'\r\n')
 assert data.count(old_bytes)==1;p.write_bytes(data.replace(old_bytes,new_bytes))
path=r/'checkpoint-pebble-amend-index.patch';path.write_text(''.join(patch),encoding='utf8',newline='\n')
subprocess.run(['git','apply','--cached',str(path)],cwd=root,check=True)
print('Only the owned checkpoint paragraph was amended in index and working docs.')
