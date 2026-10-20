from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent
changes={'breakthrough-depth12-finished-20261020':'breakthrough-exact-witness-finished-20261020','breakthrough-depth12-final-gate-20261020':'breakthrough-exact-witness-final-gate-20261020','breakthrough-depth12-nonce-20261020':'breakthrough-exact-witness-nonce-20261020','breakthrough-depth12-final-20261020':'breakthrough-exact-witness-final-20261020','depth12-context-final-20261020-v1':'full259-witness-final-20261020-v1','depth12_context_cache.rs':'witness_context_cache.rs'}
for suffix,filename in[('nonce','run.py'),('final','finalize.py')]:
 old=ex/('breakthrough-depth12-'+suffix+'-20261020');r=ex/('breakthrough-exact-witness-'+suffix+'-20261020');r.mkdir(exist_ok=False)
 for n in['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
 s=(old/filename).read_text()
 for before,after in changes.items():s=s.replace(before,after)
 s=s.replace('start<7200','start<21600')
 ast.parse(s);(r/filename).write_text(s)
 (r/'PLAN.md').write_text('''# Dependent qualified nonce and unchanged benchmark after ownfinalPASS

Only final frozenfull259 arithmetic source's ownfull259-witness-final-20261020-v1
PASS/allfourchecks permits anyscreen. RecheckEVERYsource/17protected byte, source/
stream/gate hashes andfrozen exactengine/source/library/binary; new8partialnonce
controls1..8/24protectedfullstate/RNG/curve batches beforeproduction. Ascending
1..65536/8workers/64windows, lowestcompletePASS, nevercostselection. Discloseall
completed screens/control repetitions/windowoverrun; selectedprotected9024PASS.
Finalsource changesONLYwitness_context_cache::IDENTITY_NONCE0->selectednonce.
Unchangedoriginalbenchmark.sh mustrebuild andPASS9024shots; everyprefixbyte and
all96identitytail operands checked; historicalresults restored. Thencomplete
source/evidencearchive andindependentlocalmemberverification/freshcurrentT
minimumcheck beforeauthorizedautomaticGPT-6sol/Codex upload. No oldgateverdict
or sourceindices reused. Globalproduct goalremainsactive afterindependentTgain.
''')
 print(r)
