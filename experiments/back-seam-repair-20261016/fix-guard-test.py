from pathlib import Path
import shutil,subprocess
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016')
shutil.copy2(r/'guard-tests.log',r/'guard-tests-first-mutation-index-negative.log');shutil.copy2(r/'guard-tests.exit',r/'guard-tests-first-mutation-index-negative.exit');shutil.copy2(r/'back_seams.rs',r/'back_seams-first-guard-test.rs')
for p in[r/'back_seams.rs',r/'candidate/src/point_add/back_seams.rs']:
 s=p.read_text();needle='b[0].c_target=BitId(99999);static_contract(&a,&b);';assert s.count(needle)==1;p.write_text(s.replace(needle,'let i=b.iter().position(|o|o.kind==K::Hmr).unwrap();b[i].c_target=BitId(99999);static_contract(&a,&b);'))
(r/'candidate-source.patch').write_bytes(subprocess.check_output(['git','-C',str(r/'candidate'),'diff','--binary']))
