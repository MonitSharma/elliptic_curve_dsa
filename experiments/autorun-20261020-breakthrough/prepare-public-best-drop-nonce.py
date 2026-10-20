from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-groups-context-nonce-20261020';r=a.parent/'breakthrough-public-best-drop-nonce-20261020';r.mkdir(exist_ok=True);assert not(r/'run.py').exists()
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace('breakthrough-groups-context-finished-20261020','breakthrough-public-best-drop-finished-20261020').replace('breakthrough-groups-context-final-gate-20261020','breakthrough-public-best-drop-final-gate-20261020').replace('groups-context230-final-20261020-v1','public-best-drop-product-final-20261020-v1').replace("'65536','8'","'65536','32'")
needle="'unique_nonce_controls':8,";assert s.count(needle)==2;s=s.replace(needle,"'workers':32,"+needle,1);ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Qualified initial ascending nonce prefix for the gate-passing Q1233 product source

Sole gate public-best-drop-product-final-20261020-v1 PASS131072x64/source:
same14105 wrongvalue IDs as exactpublicacd0, dirty0, McNemarp.2123667109,
17.732574failedbatches/packet <=18. Preserve verdict unchanged. Final source
b2a01786/nonce0 stream61927788, Q1233, resource-selected exactr012 plus113new
existing-wire caches. No new packet/circuit/window changes after frozen gate.

Recheck complete source/stream/gate and exactengine/library/binary hashes before
any screening. QUALIFY eightpartialnoncecontrols1..8,24protected fullstate/RNG
batches0/70/140; these repeatinproduction. Only then exactfullstate rejection
search ascending1..65536,32workers/windows64, lowestfullPASS, no cost selection.
Retain every screen, passes and completed-window overrun. Passingnonce separately
requiresprotected9024-attempt replay and unchangedfullbenchmark/localreview.
If no pass, preserve exact exhausted-prefix result; any continuation must start
at65537 on unchangedsource/gate and disclose allprefixes. No new gate/census.
''');print(r)
