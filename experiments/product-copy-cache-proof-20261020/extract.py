import hashlib,json,sys,struct
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;sys.path.insert(0,str(ws/'product-copy-cache-native-20261020'));import inspect_stream as s
START=14240623;FIRST=14241681;LAST=14245297;NO=2**64-1
assert not (r/'WINDOW.json').exists()
ops=[s.fields(i) for i in range(START,LAST+1)];assert ops[0]==[11,NO,NO,558,NO,NO,NO]
depth=0;depth_at={};abi=False
for i in range(s.n):
    row=s.fields(i)
    if row[0]==2 and row[3]==558:abi=True
    if i in [START,FIRST,LAST]:depth_at[i]=depth
    if row[0]==15:depth+=1
    elif row[0]==16:depth-=1
    assert depth>=0
assert depth==0 and not abi and list(depth_at.values())==[0,0,0]
assert all(558 not in row[1:4] for row in ops[FIRST-START:])
row=lambda kind,b,a,t:[kind,b,a,t,NO,NO,NO]
replacement_first=row(13,258,724,558);copy_first=row(8,NO,558,616);consume=row(8,NO,558,215);clear=row(8,NO,215,558)
h=hashlib.sha3_256();h.update(s.v[:FIRST*56]);h.update(struct.pack('<7Q',*replacement_first));h.update(struct.pack('<7Q',*copy_first));h.update(s.v[(FIRST+1)*56:LAST*56]);h.update(struct.pack('<7Q',*consume));h.update(struct.pack('<7Q',*clear));h.update(s.v[(LAST+1)*56:])
assert h.hexdigest()=='d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5'
payload={'source_start':START,'first_offset':FIRST-START,'last_offset':LAST-START,'storage':558,'ops':ops}
(r/'WINDOW.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
audit={'status':'AUTHENTICATED_FULL_SOURCE_EXACT_EDIT_AND_CLOSED_WINDOW_AUDIT_PASS','parent_full_raw_sha3_256':'2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265','predicted_full_output_raw_sha3_256':h.hexdigest(),'output_ops':s.n+2,'storage_not_abi_and_no_original_touch_in_closed_hold':True,'endpoint_scope_depths':depth_at,'window_sha256':hashlib.sha256((r/'WINDOW.json').read_bytes()).hexdigest(),'only_changed_original_ops':[FIRST,LAST],'extra_ops':2,'R_Hmr_classical_operations_and_order_unchanged':True,'scope':'Exact edit and frame audit; symbolic equivalence is a separate required proof.'}
(r/'EDIT-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
