"""Record completed diagnostic outcomes without promoting them to resource records."""
import hashlib,json
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
reports={
 'product-lease-footprint-20261020':'''## Completed read-only diagnostic

Exit0, four controls PASS,16.68s. Highest role1233 has48767 quantum touches.
3441 unconditional-reset epochs cover48765 touches; three span2.21–2.49m
operations with no untouched non-ABI donor, and two trailing uses remain
outside those lexical epochs. Donor inactivity alone proves no value identity.
Full265277386-byte raw JSON is retained locally/server and preserved losslessly
inside the verified34.5MB evidence archive; raw JSON is ignored by Git.
No lease, candidate, width saving, statistical gate, nonce or record.

''',
 'product-clean-lease-probe-20261020':'''## Completed exact baseline-controlled diagnostic

Exit0. Baseline12 controls and instrumented15 controls PASS. Every original
report/counter field and complete recolored output hash match exactly.
Strong proved-clean boundaries cover all48767 touches in4350 semantic epochs;
three still have no untouched non-ABI donor. First full-width post-state is
source op1444755. The full verified archive is preserved. No held-value
identity, lease implementation, width reduction, gate, nonce or scored result.

''',
 'product-peak-parity-probe-20261020':'''## Completed fixed first-peak method negative

Exit0,17 controls per baseline/snapshot copy PASS, exact prefix/global-ABI/
atom/cut/site control. Before/after source op1444755, all1233 non-high rows
have exact rank1233 in the fixed cap256/degree12 universal ANF abstraction.
No linear relation or idle parity donor is certified. Independent local
elimination with the opposite pivot order reproduces both ranks. All34 archive
members, original snapshots, sources, tests and hashes are verified.
This is not a physical quantum-width lower bound. Do not repeat this fixed
probe or implement a parity lease from its uncertified relations. No circuit,
statistical gate, nonce or resource result. Its frozen cache input separately
failed its own final statistical gate; that verdict stays final.

'''}
for name,block in reports.items():
 r=ws/name;assert (r/'LOCAL-VERIFICATION.json').exists();p=r/'STATUS.md';raw=p.read_bytes()
 try:old=raw.decode('utf-8')
 except UnicodeDecodeError:
  old=raw.decode('cp1252')
  (r/'STATUS-ENCODING.json').write_text(json.dumps({'original_encoding':'Windows cp1252','original_sha256':hashlib.sha256(raw).hexdigest(),'original_bytes_preserved_in':'evidence.tar.gz','current_completed_report_encoding':'UTF-8','source_and_proof_files_unchanged':True},indent=2)+'\n')
 if block not in old:
  h,t=old.split('\n',1);p.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n')
print('Finished diagnostic statuses; no component result promoted to a resource record')
