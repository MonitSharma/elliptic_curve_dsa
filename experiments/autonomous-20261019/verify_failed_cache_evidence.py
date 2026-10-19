"""Preserve the failed verdict unchanged, with zero post-gate nonce evaluations."""
import hashlib,json,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-copy-cache-native-20261020';info=json.loads((r/'GATE-EVIDENCE.json').read_text());p=r/info['archive']
sha=hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert sha==info['sha256'] and info['gate_status']=='FAILURE_GATE_FAIL'
with tarfile.open(p) as a:
 files=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))['included_files'];assert len(files)==17
 for key,v in files.items():
  assert a.getmember(key).size==v['bytes'] and hashlib.file_digest(a.extractfile(key),'sha256').hexdigest()==v['sha256']
 for key in ['qualification/DECLARATION.json','qualification/RESULT.json','GATE-AUDIT.json']:
  out=r/'gate-receipts'/key;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(a.extractfile(key).read())
verdict=json.loads((r/'gate-receipts/qualification/RESULT.json').read_text());audit=json.loads((r/'gate-receipts/GATE-AUDIT.json').read_text())
assert verdict['status']==audit['gate_status']=='FAILURE_GATE_FAIL'
assert verdict['rules']=={'value_not_above_parent':True,'paired_mcnemar_p_at_least_005':False,'failed_batches_per_packet_at_most_18':True,'zero_dirty_shots':True}
assert verdict['mcnemar_one_sided_p']==0.017701059294805803 and audit['no_new_census_or_verdict_change']
refusal=json.loads((ws/'product-copy-cache-filter-20261020/WATCH_RESULT.json').read_text());assert refusal['status']=='DISABLED_QUALIFICATION_REFUSED_BUILD_OR_FINAL_GATE' and not refusal['new_source_nonce_tests_started'] and refusal['verdict_is_final_no_rerun']
(r/'LOCAL-GATE-VERIFICATION.json').write_text(json.dumps({'status':'FINAL_FAILED_GATE_ARCHIVE_ALL_MEMBERS_AND_REFUSAL_VERIFIED','files':17,'sha256':sha,'gate_verdict_final':True,'new_source_nonce_tests_started':False,'no_benchmark_or_record':True},indent=2)+'\n')
message='''## Final circuit eligibility: FAILED statistical gate

The sole262144x64 gate, pareto-parent4-copy-cache-gate-20261020-v1, failed
the paired McNemar requirement: b2973,c2812,p0.017701059294805803.
Value-failing shots28835=28835,dirty0, and failed batches perpacket
17.991291046142578 satisfy the other three rules. This verdict is final.
No relabel, larger census, rerun or nonce search is permitted on this circuit.
The disabled runtime waiter refused before any new-source nonce evaluation.
Complete original rows, source/stream hashes and independent exact-count audit
are preserved in gate-evidence.tar.gz; every member verified locally.
The universal one-T component theorem still holds, but it is not an eligible
full-circuit record. The separately qualified classical12 circuit excludes
this failed extra cache change and retains its own passing verdict.

'''
for folder in [r,ws/'product-copy-cache-filter-20261020',ws/'product-copy-cache-proof-20261020']:
 path=folder/'STATUS.md'
 if not path.exists():path.write_text('# Research status\n\n'+message,encoding='utf-8',newline='\n')
 else:
  old=path.read_text(encoding='utf-8')
  if message not in old:
   h,t=old.split('\n',1);path.write_text(h+'\n\n'+message+t.lstrip('\n'),encoding='utf-8',newline='\n')
print('Failed gate final; all524288 existing rows preserved and zero new-source nonce evaluation verified')
