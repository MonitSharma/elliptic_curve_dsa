"""Verify the sealed counts satisfy the originally declared four rules."""
import hashlib,json
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-classical-nine-20261019';q=r/'qualification'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
audit=json.loads((r/'GATE-AUDIT.json').read_text());v=json.loads((q/'RESULT.json').read_text());d=json.loads((q/'DECLARATION.json').read_text())
assert sha(q/'RESULT.json')==audit['verdict_sha256'] and sha(q/'DECLARATION.json')==audit['declaration_sha256']
assert audit['all_rows_unique_complete_unskipped'] and audit['exact_integer_mcnemar_tail_matches']
assert v['batches']==d['batch_count']>=32768 and d['shots_per_batch']==64
actual={'value_not_above_parent':v['value_shots']['candidate']<=v['value_shots']['parent'],
 'paired_mcnemar_p_at_least_005':v['mcnemar_one_sided_p']>=.05,
 'failed_batches_per_packet_at_most_18':141*v['failed_batches']['candidate']<=18*v['batches'],
 'zero_dirty_shots':v['dirty_shots']['candidate']==0}
assert actual==v['rules'] and all(actual.values())
assert all(141*n/v['batches']==v['failed_batches_per_packet'][name] for name,n in v['failed_batches'].items())
result={'status':'ALL_FOUR_ORIGINAL_RULES_VERIFIED_FROM_AUDITED_SEALED_COUNTS','rules':actual,'row_audit_sha256':sha(r/'GATE-AUDIT.json'),'sealed_verdict_sha256':sha(q/'RESULT.json'),'driver_sha256':sha(Path(__file__)),'no_new_rows_label_nonce_or_verdict_change':True}
(r/'GATE-RULES-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
