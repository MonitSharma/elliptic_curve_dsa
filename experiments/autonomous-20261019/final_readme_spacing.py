"""Polish only the new result paragraph, preserving unstaged README changes."""
import difflib,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1]
changes={'All9,024 shots pass.':'All 9,024 shots pass.','lowest passing nonce7,614,812':'lowest passing nonce 7,614,812','accounting of7,811,072':'accounting of 7,811,072'}
old=subprocess.check_output(['git','show',':README.md'],cwd=root).decode();new=old
for a,b in changes.items():assert new.count(a)==1;new=new.replace(a,b)
(r/'final-readme-spacing.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/README.md',tofile='b/README.md')),encoding='utf-8',newline='\n')
for path in [root/'README.md',r/'write_classical12_result.py']:
 s=path.read_text(encoding='utf-8')
 for a,b in changes.items():assert s.count(a)==1;s=s.replace(a,b)
 path.write_text(s,encoding='utf-8',newline='\n')
print('Polished only the new README result paragraph')
