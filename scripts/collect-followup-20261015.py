"""Collect compact local evidence from the completed follow-up's copied logs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
dest=root/'experiments/followup-20261015'
raw=root/'research-output/followup-20261015'
paired={}
for family in ('independent','structured','candidate'):
    p=raw/(family+'.log');text=p.read_text()
    summary=[s for s in text.splitlines() if s.startswith('DIAGNOSTIC_ONLY ')]
    assert len(summary)==1
    values={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',summary[0])}
    assert values['unequal_batches']==0
    assert values['left_bad']==values['right_bad']
    for channel in ('phase_shots','phase_batches','dirty_batches'):
        assert values['left_'+channel]==values['right_'+channel]
    assert 'Exit status: 0' in text
    paired[family]=dict(**values,log_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
receipt=json.loads((dest/'full-benchmark-receipt.json').read_text())
assert receipt['status']=='failed' and receipt['qualified_score'] is None
assert receipt['failure_counts']==dict(classical_mismatches=16,phase_garbage_batches=9,ancilla_garbage_batches=0)
assert paired['candidate']['shots']==9024
assert paired['candidate']['right_bad']==16 and paired['candidate']['right_phase_batches']==9
assert hashlib.sha256((raw/'benchmark.log').read_bytes()).hexdigest()==receipt['log']['sha256']
paired_report=dict(status='complete_paired_agreement_inherited_failures_not_qualified',
                  baseline_revision=receipt['baseline_revision'],candidate_stream_sha256=receipt['stream']['sha256'],
                  packets=paired,bindings=(raw/'bindings.sha256').read_text(),
                  packet_hashes=(raw/'packets.sha256').read_text(),qualified_score=None,
                  independent_packet_scope='Existing fixed B3 domain independent of stream hashes; reused, not freshly selected',
                  server_directory='/home/hclau/ecdsa_research/followup-20261015/guarded-zero-paired')
(dest/'paired-receipt.json').write_text(json.dumps(paired_report,indent=2)+'\n')
schedule=json.loads((raw/'b3-early-measurement.json').read_text())
schedule['proposed_move_count']=len(schedule.pop('moves'))
schedule['raw_file_sha256']=hashlib.sha256((raw/'b3-early-measurement.json').read_bytes()).hexdigest()
(dest/'early-measurement-summary.json').write_text(json.dumps(schedule,indent=2)+'\n')
sources=['audit-structural-sharing.py','audit-early-measurement.py','search-proved-resubstitution.py',
         'test_proved_resubstitution.py','verify-resubstitution-proofs.py','verify-guarded-zero-stream.py',
         'explain-guarded-zero.py','prepare-final-pass-audit.py','server-final-pass-audit.sh',
         'server-guarded-zero-candidate.sh','server-guarded-zero-benchmark-v2.sh','server-guarded-zero-paired.sh',
         'server-proved-resubstitution.sh','server-structural-sharing.sh','stop-followup-trial.py',
         'analyze-guarded-lifetimes.py','analyze-wire-lifetimes.py','test_guarded_lifetimes.py',
         'research-receipt.py','prepare-wire-zero-audit.py','collect-followup-20261015.py','review-bankswap-terminal.py']
files=[root/'scripts'/s for s in sources]+[p for p in dest.rglob('*') if p.is_file() and p.name!='manifest.json']
manifest=dict(collected_at_utc=datetime.now(timezone.utc).isoformat(),status='b3_gate_candidate_failed_bankswap_width_candidate_local_pass',
              b3_qualified_score=None,bankswap_review='bankswap-terminal/reviewed-receipt.json',
              files={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'paired':paired,'artifact_files':len(files),'qualified_score':None},indent=2))
