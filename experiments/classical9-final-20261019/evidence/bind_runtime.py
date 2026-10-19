import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;s=r.parent/'product-classical-nine-operational-20261019'
assert json.loads((s/'CONTROL.json').read_text())['status']=='CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX'
a=s/'ACCEPTANCE.json';acc=json.loads(a.read_text());assert acc['status']=='SOURCE_BOUND_MASK_TRANSFER_AND_RUNTIME_ACCEPTED_FOR_ASCENDING_SEARCH'
assert acc['candidate_stream_sha256']=='76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
h,b=sha(a),sha(s/'tool/target/release/value_prefilter');assert b==acc['operational_binary_sha256']
p=r/'audit-terminal.py';src=p.read_text();assert src.count('UNBOUND_NOT_ACCEPTED')==2
src=src.replace("ACCEPTANCE='UNBOUND_NOT_ACCEPTED'","ACCEPTANCE='"+h+"'").replace("BINARY='UNBOUND_NOT_ACCEPTED'","BINARY='"+b+"'");p.write_text(src)
(r/'RUNTIME-BINDING.json').write_text(json.dumps({'status':'RUNTIME_PINNED_AFTER_OWN_PREFIX_CONTROL','acceptance_sha256':h,'binary_sha256':b,'auditor_sha256':sha(p),'complete_path_audit_required_before_watch':True},indent=2)+'\n')
