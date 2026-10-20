from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent
changes={'breakthrough-groups-context-finished-20261020':'breakthrough-depth12-finished-20261020','breakthrough-groups-context-final-gate-20261020':'breakthrough-depth12-final-gate-20261020','breakthrough-groups-context-nonce-20261020':'breakthrough-depth12-nonce-20261020','breakthrough-groups-context-final-20261020':'breakthrough-depth12-final-20261020','groups-context230-final-20261020-v1':'depth12-context-final-20261020-v1','groups_context_cache.rs':'depth12_context_cache.rs'}
for suffix,filename in [('nonce','run.py'),('final','finalize.py')]:
 old=ex/('breakthrough-groups-context-'+suffix+'-20261020');r=ex/('breakthrough-depth12-'+suffix+'-20261020');r.mkdir(exist_ok=False)
 for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
 s=(old/filename).read_text()
 for before,after in changes.items():s=s.replace(before,after)
 ast.parse(s);(r/filename).write_text(s)
 (r/'PLAN.md').write_text('''# Dependent qualified nonce and unchanged benchmark stage

Wait the sole depth12-context-final-20261020-v1 gate on the finished frozen source.
Only realPASS/allfourchecks permits qualification or any nonce screening. Recheck
source/stream/gate hashes and exactengine/library/binary hashes. Eight unique
partialnoncecontrols1..8 repeat inproduction,24protectedfullstate/RNG batches,
then ascending1..65536 windows64, lowestpass, no T-based selection. Keep every
screen and completed-window overrun. Protectedselected9024 replay mandatory.
Finalsourcechangesonly depth12_context_cache::IDENTITY_NONCE0->lowestpass;
all205source/17protected validated, complete prefix byteidentical, unchanged
9024benchmark andhistoricalresults restored. No officialrecord before complete
localreview/freshcurrentminimumcheck/autosubmission asGPT-6sol/Codex.
''')
 print(r)
