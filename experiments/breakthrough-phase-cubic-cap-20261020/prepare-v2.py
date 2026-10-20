"""Scope every edit to T0Phase after the first preparation stopped safely."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';old=r.parent/'breakthrough-direct-transport-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE-v2.json').read_text())
assert(r/'run.exit').read_text().strip()=='1';assert not(r/'SOURCE_FREEZE.json').exists();assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
failed=r/'failed-ambiguous-edit-v1';failed.mkdir(exist_ok=False);shutil.copyfile(r/'prepare.log',failed/'prepare.log')
s=(r/'prepare.py').read_text();s=s.replace('assert not t.exists()and(', 'assert t.exists()and(')
start=s.index("subprocess.run(['git','-C'");end=s.index("p=t/'src/point_add/y15_onefold.rs'",start);s=s[:start]+s[end:]
needle=" assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)";assert s.count(needle)==1
replacement=" start=raw.index(b'struct T0Phase {');end=raw.index(b'\\n}\\n',raw.index(b'impl T0Phase {',start))+3;region=raw[start:end]\n assert region.count(a)==1,(a,region.count(a));raw=raw[:start]+region.replace(a,b)+raw[end:]"
s=s.replace(needle,replacement);(r/'adapted-prepare-v2.py').write_text(s);exec(compile(s,str(r/'adapted-prepare-v2.py'),'exec'))
