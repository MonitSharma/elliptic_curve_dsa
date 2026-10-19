"""Stage only this checkpoint, preserving pre-existing working-tree doc edits."""
import ast,difflib,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1]
tree=ast.parse((r/'sync_checkpoint.py').read_text(encoding='utf-8'));block=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='block' for t in n.targets))
chunks=[]
for name in ('docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md'):
    old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode('utf-8')
    head,tail=old.split('\n',1);new=head+'\n\n'+block+tail.lstrip('\n')
    chunks.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
(r/'checkpoint-docs.patch').write_text(''.join(chunks),encoding='utf-8',newline='\n')
