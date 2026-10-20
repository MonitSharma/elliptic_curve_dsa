from pathlib import Path
import ast,shutil
root=Path(__file__).resolve().parents[2];ex=root/'experiments';oldprefix='breakthrough-public322-square';newprefix='breakthrough-context-lease';label='context213-exact-earlier-cut-final-20261020-v1'
g=ex/(newprefix+'-final-gate-20261020');g.mkdir(exist_ok=False)
for filename in['census.py','run.py']:shutil.copyfile(ex/(oldprefix+'-final-gate-20261020')/filename,g/filename)
s=(ex/(oldprefix+'-final-gate-20261020')/'declare.py').read_text()
changes={oldprefix+'-finished-20261020':newprefix+'-finished-20261020',"'32256595-e0a3-4015-96ab-3422c866ec48'":"'a4ee760a-0500-4d54-9822-4a3c56806fd5'","'toffoli':751020":"'toffoli':750911'",'63d63c90a25e204d3173d5078f5a0bf12c9d65b7':'be2902c2a133754968dbc97992c753cc08730e83',"a['native_tests']==27 and a['diagnostic_weight']<751022.25":"a['native_tests']==28 and a['diagnostic_weight']<750900",'finished_square_pipeline.rs':'context_finished.rs','breakthrough-public8b-repeat-final-20261020/PUBLIC-SOURCE-VERIFICATION.json':'breakthrough-public322-square-final-20261020/PUBLIC-SOURCE-VERIFICATION.json','6a8af77b4b0f7e428d52759d555737493dfbf2803a58e0e53d4268557c9fb36f':'54c8cd60337d1afaa36ff37ae0b29f321838df707350704def8a02e3e8716e69','public322-square1408-final-20261020-v1':label,'Sole final gate on this independent square1408 finished source.':'Sole final gate on this independent context213 finished source.','Previous repeat-generic gate is historical, not reused.':'Previous parent square gate is historical, not reused.'}
changes["'toffoli':751020"]="'toffoli':750911"
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
start=s.index("'scope':'Existing exact square workspace1234->1408;");s=s[:start]+"'scope':'Whole officiala4ee constructor byte-preserved, full parent binding,213 independently exact earlier-context unconditional leases with full output binding, unchanged generic pass, nonce0.28 native controls pass. Extra width allowed for independent T objective; no arithmetic/precision/cut changes. No benchmark/nonce yet.'}"+s[s.index(";(r/'GATE-DECLARATION.json')",start):]
ast.parse(s);(g/'declare.py').write_text(s)
n=ex/(newprefix+'-nonce-20261020');n.mkdir(exist_ok=False);f=ex/(newprefix+'-final-20261020');f.mkdir(exist_ok=False)
for target,filename in[(n,'run.py'),(f,'finalize.py')]:
 source=(ex/(oldprefix+('-nonce-20261020'if target==n else'-final-20261020'))/filename).read_text();source=source.replace(oldprefix+'-nonce-20261020',newprefix+'-nonce-20261020').replace(oldprefix+'-finished-20261020',newprefix+'-finished-20261020').replace(oldprefix+'-final-gate-20261020',newprefix+'-final-gate-20261020').replace(oldprefix+'-final-20261020',newprefix+'-final-20261020').replace('public322-square1408-final-20261020-v1',label).replace('finished_square_pipeline.rs','context_finished.rs');ast.parse(source);(target/filename).write_text(source)
for p in[g,n,f]:(p/'.gitattributes').write_text('* -text\n');(p/'.gitignore').write_text('candidate/\ntool/\n__pycache__/\n*resource-preflight*\npublic-before-upload.json\n')
print('Prepared exactcontext sole gate, qualified ascending nonce, and final unchanged benchmark controllers; not launched.')
