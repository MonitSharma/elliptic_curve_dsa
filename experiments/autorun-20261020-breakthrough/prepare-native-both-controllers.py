from pathlib import Path
import ast,shutil
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];ex=root/'experiments';oldprefix='breakthrough-context-lease';newprefix='breakthrough-native-both';label='native-rail-g6-fixed-final-20261020-v1';g=ex/(newprefix+'-final-gate-20261020');g.mkdir(exist_ok=True)
for name in['census.py','run.py']:assert not(g/name).exists();shutil.copyfile(ex/(oldprefix+'-final-gate-20261020')/name,g/name)
for suffix,filename in[('nonce','run.py'),('final','finalize.py')]:
 r=ex/(newprefix+'-'+suffix+'-20261020');r.mkdir(exist_ok=True);assert not(r/filename).exists();s=(ex/(oldprefix+'-'+suffix+'-20261020')/filename).read_text();s=s.replace(oldprefix+'-finished-20261020',newprefix+'-finished-20261020').replace(oldprefix+'-final-gate-20261020',newprefix+'-final-gate-20261020').replace(oldprefix+'-nonce-20261020',newprefix+'-nonce-20261020').replace(oldprefix+'-final-20261020',newprefix+'-final-20261020').replace('context213-exact-earlier-cut-final-20261020-v1',label).replace('context_finished.rs','native_both_finished.rs')
 if suffix=='final':
  # The unchanged benchmark itself performs the selected-source rebuild. Verify
  # every pre-tail byte after that build; avoid a redundant full nine-minute run.
  a=" run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'native-build')\n run([str(t/'target/release/build_circuit')],'native-generate')\n";assert s.count(a)==1;s=s.replace(a,'');a=" first=receipt();save('NATIVE-RECEIPT.json',first)\n";assert s.count(a)==1;s=s.replace(a,'');a=' assert receipt()==first';assert s.count(a)==1;s=s.replace(a," first=receipt();save('NATIVE-RECEIPT.json',first)")
 ast.parse(s);(r/filename).write_text(s);(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('candidate/\ntool/\n__pycache__/\n*resource-preflight*\npublic-before-upload.json\n')
(g/'.gitattributes').write_text('* -text\n');(g/'.gitignore').write_text('__pycache__/\n*resource-preflight*\n')
log=f'\n{datetime.now(timezone.utc).isoformat()} predeclare fixed nativeboth final gate native-rail-g6-fixed-final-20261020-v1,32768x64 vs exact then-current context213 official T parent; wait pending260b result and public198/17 byteverify beforedeclaration, neverreusecontextgate. Candidate200/17,27controls,raw+allgenericrecordsbound,a871 nonce0. PASS only→independent8nonce/24statequalification→ascendinglowest→unchangedbenchmarkonce verifiesallpre-tailbytes→localreview→autosubmitGPT6sol/Codex.\n';p=ex/'autorun-20261020-breakthrough/LOG.md';p.write_bytes(p.read_bytes().rstrip()+log.encode());print('Prepared new sole gate and independently qualified nonce/benchmark controllers; no gate declared yet.')
