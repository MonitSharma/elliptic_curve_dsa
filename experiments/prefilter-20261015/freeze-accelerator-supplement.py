from pathlib import Path
import json,hashlib,datetime
r=Path(__file__).parent;e=r/'evidence'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def rec(p):return dict(path=str(p.relative_to(r)),bytes=p.stat().st_size,sha256=sha(p))
for stem in ['global-anf-mask-partial','mask-validate-transfer','mask-slot-compile','mask-slot-validate','mask-fusion-profile','mask-fused-compile','mask-fused-validate']:assert (e/(stem+'.exit')).read_text().strip()=='0'
assert sha(e/'mr-mask-tip-v3.bin')==sha(e/'mr-mask-tip-v4-partial.bin')=='560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d'
for stem in ['global-anf-mask-partial','mask-validate-transfer']:assert (e/(stem+'-before.sha256')).read_bytes()==(e/(stem+'-after.sha256')).read_bytes()
reports={s:json.loads((e/(s+'.json')).read_text()) for s in ['mask-slot-verification','mask-slot-runtime','mask-fusion-profile','mask-fused-verification','mask-fused-runtime','global-anf-mask-partial-tip32']}
transfer={s:json.loads((e/('mask-validate-transfer-'+s+'.json')).read_text()) for s in ['audit','all-failing-tip','sensitivity-structured','sensitivity-arbitrary']}
assert sum(v['shots'] for v in transfer.values())==2214 and all(v['candidate_protected_vs_original_zeroMR_known_bit_containment_passed'] for v in transfer.values())
assert reports['mask-fused-runtime']['compared_words']==393216
files=[r/x for x in ['mask_slots.c','mask_slots.h','libmask_slots.so','mask_fused.c','mask_fused.h','libmask_fused.so','compile-mask-slots.py','verify-mask-slots.py','bench-mask-slots.py','compile-mask-fused.py','verify-mask-fused.py','bench-mask-fused.py','profile-mask-fusion.py']]+[e/x for x in ['mr-mask-tip-v3-slots.bin','mr-mask-tip-v3-slots.nodeids-u32le.bin','mr-mask-tip-v3-fused.bin','mr-mask-tip-v3-fused.nodeids-u32le.bin']]
report=dict(status='TERMINAL_VALIDATED_SOURCE_CERTIFICATE_UNCHANGED_RUNTIME_SUPPLEMENT',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_mask_sha256=sha(e/'mr-mask-tip-v3.bin'),original_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',candidate_stream_sha256='180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64',partial_proof_output_byte_identical=True,partial_tests=38,partial_protected_containment_seeds=4,transfer_finite_replays_supplement_universal_certificate=True,transfer=transfer,reports=reports,artifacts=[rec(p) for p in files],live_search_launched_by_this_agent=False,record_claim=False)
(e/'accelerator-supplement-freeze.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(receipt='evidence/accelerator-supplement-freeze.json',sha256=sha(e/'accelerator-supplement-freeze.json'))))
