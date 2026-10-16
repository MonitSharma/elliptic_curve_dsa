from pathlib import Path
import hashlib,json,tarfile

R=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
receipt=json.loads((R/'ARCHIVE-RECEIPT.json').read_text())
assert sha((R/'evidence.tar.gz').read_bytes())==receipt['archive_sha256']
with tarfile.open(R/'evidence.tar.gz')as tar:
 manifest=json.loads(tar.extractfile('MANIFEST.json').read())
 assert len(manifest)==receipt['verified_members']
 for name,h in manifest.items():assert sha(tar.extractfile(name).read())==h,name
 assert sha(tar.extractfile('TERMINAL-RECEIPT.json').read())==receipt['terminal_receipt_sha256']
 terminal=json.loads(tar.extractfile('TERMINAL-RECEIPT.json').read())
 assert terminal['run_exit']==0 and terminal['all65536complete_trial_rows_equal']
 report={'status':'LOCAL_INDEPENDENT_ARCHIVE_MANIFEST_PASS','archive_sha256':receipt['archive_sha256'],
  'verified_members':len(manifest),'terminal_receipt_sha256':receipt['terminal_receipt_sha256'],
  'run_exit':terminal['run_exit'],'all65536complete_trial_rows_equal':True}
(R/'LOCAL-ARCHIVE-VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
