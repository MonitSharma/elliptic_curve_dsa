from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-exact-native-ports-v2-20261020';r=root/'experiments/breakthrough-exact-native-ports-v3-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','PLAN.md','rail-tests.rs','run.py']:shutil.copyfile(old/p,r/p)
s=(old/'prepare.py').read_text();a="raw=raw.replace(oldblock,b'        if std::env";assert s.count(a)==1;s=s.replace(a,"raw=raw.replace(oldblock,b'        let bit0=if std::env")
a=r"+newblock+b'\n        }else{\n'+oldblock+b'\n        }');";assert s.count(a)==1;s=s.replace(a,r"+newblock+b'\n            bit0\n        }else{\n'+oldblock+b'\n            bit0\n        };');");(r/'prepare.py').write_text(s)
(r/'REPAIR-NOTE.md').write_text('''The v2 frozen source failed compilation before any test ran: its research
runtime selector scoped bit0 inside each G6 branch, while the unchanged following
free_bit(bit0) needs the common binding. Both branches now return that existing
BitId into let bit0. The original public arithmetic blocks are unchanged, both
still free their original internal bits, and the outer cleanup remains intact.
Earlier source/freezes/compiler failures remain untouched. No gate/nonce or
circuit verdict is re-run. The v1 empty-hunk parser failure also remains.
''');print(r)
