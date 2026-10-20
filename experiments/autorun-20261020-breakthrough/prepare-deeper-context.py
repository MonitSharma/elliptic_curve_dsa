from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-context-lease-20261020';r=root/'experiments/breakthrough-context16384-lease-20261020';r.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
(r/'PLAN.md').write_text('''# Larger exact earlier-cut context

The4096-operation context engine independently proves213 new unconditional
leases on the frozen officiala4ee stream54c8cd60 after7 native/fault controls.
Test a fixed16384-operation lookback on the SAME finished input, retaining the
same arbitrary-cut algebra, same-scope boundary, full equality acceptance,
65536-expression knowledge cap, donor budget16 and phase rewrite. No quantum
circuit content/input/cut is tuned to a packet. This is an exact proof search
parameter; any accepted rewrite still requires full symbolic proof. Repeat7
native controls before full scan. One-hour bounded job, no final census/nonce.
Positive savings are component-only until separately integrated/frozen/gated
against the public record then current. Original4096 evidence remains untouched.
''')
(r/'prepare.py').write_text('''import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-context-lease-20261020';t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert(old/'run.exit').read_text().strip()=='0'and not t.exists();assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items());assert sha(Path(f['input']))==f['input_sha256'];t.mkdir()
for p in f['tool_source_files']:shutil.copyfile(old/'tool'/p,t/p)
p=t/'discover.rs';raw=p.read_bytes();a=b'first.saturating_sub(4096)';assert raw.count(a)==1;p.write_bytes(raw.replace(a,b'first.saturating_sub(16384)'));subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True);f['tool_source_files']={p.name:sha(p)for p in t.iterdir()if p.is_file()};f['context_lookback_operations']=16384;f['prior4096_freeze_sha256']=sha(old/'SOURCE-FREEZE.json');f['scope']='Fixed16384 earlier arbitrary cut within SAME lexical scope, exact equality only, unchanged donor/phase rewrite.7 native/fault controls before component scan. No gate/nonce/score.';(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\\n')
''')
shutil.copyfile(old/'run.py',r/'run.py');print(r)
