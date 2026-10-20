from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-best-drop-nonce-20261020';r=a.parent/'breakthrough-public-best-drop-nonce-v2-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace("'65536','32'","'65536','16'").replace("'workers':32","'workers':16");ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Same frozen product source and passed gate; supported exact-engine thread count

Originalnonce-driver requested32threads, but the existing qualified engine
rejects CLIthreads>16 before controls or screening. Originalrun.exit1 and
qualification.exit101/parserassertion preserved. Zero completed nativecontrols,
zero production screens and no selected nonce occurred in that setup attempt.
The circuit/sourceb2a01786, literalnonce0stream61927788, sole131072batch PASS
and every gate datum are unchanged; no new label/census/source/nonce tuning.

V2 uses supported16threads, rechecks all source/gate/engine/library hashes,
qualifies eightpartial1..8 controls/24protectedfullstate/RNGbatches, then ascending
1..65536/windows64 lowestPASS. Keepallproductionrows/overrun, no T selection.
Passingnonce needsprotected9024replay and unchangedbenchmark/localreview before
officialsubmission. Any latercontinuation startsafter65536 on samefrozencircuit,
preserving this initialprefix andallcounts. Correctedsetup is not a gate rerun.
''');print(r)
