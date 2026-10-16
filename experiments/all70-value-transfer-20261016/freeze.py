import hashlib,json,tarfile
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(R/'run.exit').read_text().strip()=='0' and(R/'supplement.exit').read_text().strip()=='0'
a=json.loads((R/'CLASSIFICATION.json').read_text());b=json.loads((R/'SWAP-REFINEMENT.json').read_text())
assert len(a['sites'])==70 and len(b['reports'])==7
assert all(x['status']=='UNKNOWN_VALUE_CONTROL_FANOUT_AFTER_SWAP'for x in b['reports'])
assert a['summary']=={'UNKNOWN_VALUE_CONTROL_OR_SWAP_FANOUT':63,'UNKNOWN_VALUE_TARGET_OPERATION':7}
for name,h in json.loads((R/'DECLARATION.json').read_text())['pins'].items():assert sha(R.parent/name)==h
receipt={'status':'TERMINAL_NEGATIVE_SIMPLE_PHASE_ONLY_VALUE_TRANSFER','authority':False,'all_sites':70,
 'direct_value_control_before_unconditional_reset':63,'unconditional_swap_then_value_control_before_reset':7,
 'admitted_phase_only_reset_frames':0,
 'interpretation':'Every restoration target has a structural value fanout before reset, including7propagated through3exact unconditionalSWAPs. This does not prove a finalvaluechange; wholehelper cancellation may still allow a contract. No original mask transfer follows.',
 'historical_marker':'Initial synchronous supplement shell wroteTrue rather than numeric exit due quoting. Logs/results preserved; separately hashed run-supplement.sh reran identical source and records numeric0. No classification/source change.',
 'classification_sha256':sha(R/'CLASSIFICATION.json'),'swap_refinement_sha256':sha(R/'SWAP-REFINEMENT.json')}
(R/'TERMINAL-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=[p for p in R.rglob('*')if p.is_file()and p.name not in('evidence.tar.gz','MANIFEST.json','ARCHIVE-RECEIPT.json')]
manifest={str(p.relative_to(R)):sha(p)for p in files};(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(R/'evidence.tar.gz','w:gz')as t:
 for p in sorted(files+[R/'MANIFEST.json']):t.add(p,arcname=str(p.relative_to(R)))
with tarfile.open(R/'evidence.tar.gz')as t:
 for n,h in manifest.items():assert hashlib.sha256(t.extractfile(n).read()).hexdigest()==h
ar={'status':'VERIFIED','archive_sha256':sha(R/'evidence.tar.gz'),'verified_members':len(manifest),'terminal_receipt_sha256':sha(R/'TERMINAL-RECEIPT.json')}
(R/'ARCHIVE-RECEIPT.json').write_text(json.dumps(ar,indent=2)+'\n');print(json.dumps(ar))
