from pathlib import Path
import ast,shutil

a=Path(__file__).parent;old=a.parent/'breakthrough-public-width1233-context-20261020';r=a.parent/'breakthrough-public-width1233-context65536-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','patch-tool.py']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text();needle="subprocess.run(['python3',str(r/'patch-tool.py')],check=True);";assert s.count(needle)==1
s=s.replace(needle,needle+"raw=p.read_text();assert raw.count('first.saturating_sub(16384)')==1;p.write_text(raw.replace('first.saturating_sub(16384)','first.saturating_sub(65536)'));")
s=s.replace("'lookback':16384","'lookback':65536")
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Fixed larger exact proof context on unchanged complete width1233 stream

Original exact52a065e9 stream, no circuit, witness, window or input changes.
Increase only proof-engine same-lexical-scope arbitrary-cut lookback16384->65536.
Exact proof, no-touch/nonoverlap and donorzero requirements unchanged. All9
native value/phase/RNG/guard/fault controls repeat before scanning. Fixed zero
added wires and protected measuredQ<=1233. No point-input sampling, statistical
gate, nonce or score. Larger proof context can only nominate more sites; each
accepted replacement still needs the unchanged exact algebraic certificate.
''');print(r)
