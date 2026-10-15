"""Report three independent records; never promote a failed benchmark."""
import json
from pathlib import Path
import sys

def assess(frontier, receipt, score, replay_summaries):
    blockers=[]
    if receipt.get('status') != 'passed' or receipt.get('exit_status') != 0:
        blockers.append('The unchanged full benchmark did not pass.')
    if receipt.get('protected_tracked_changes'):
        blockers.append('Protected submission files changed.')
    if not score:
        blockers.append('No official score artifact exists.')
    if not replay_summaries:
        blockers.append('Independent replay is incomplete.')
    for family, r in replay_summaries.items():
        if any(r.get(k, -1) != 0 for k in ['unequal_batches','right_bad','right_phase_batches','right_dirty_batches']):
            blockers.append(f'{family}: correctness or equivalence checks failed.')
    improvements=[]
    metrics=None
    if not blockers:
        metrics=score['metrics'];q=metrics['qubits'];t=metrics['toffoli']
        assert type(q) is int and type(t) is int and q>0 and t>0
        assert score['score']==q*t
        leaders=frontier['leaders']
        if q < leaders['qubits']['officialMetrics']['qubits']:improvements.append('qubits')
        if t < leaders['toffoli']['officialMetrics']['toffoli']:improvements.append('toffoli')
        if q*t < leaders['product']['officialScore']:improvements.append('product')
        if not improvements:blockers.append('No new record among the three stated objectives.')
    return {'status':'READY_FOR_PACKAGING' if not blockers else 'BLOCKED',
            'record_improvements':improvements,'qualified_metrics':metrics,
            'blockers':blockers,'scalar_product_improvement_required':False}

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    wide='--wide' in sys.argv[1:]
    evidence=root/('wide-evidence' if wide else 'evidence')
    receipt=json.loads((evidence/'terminal/receipt.json').read_text())
    score_path=evidence/'score.json'
    score=json.loads(score_path.read_text()) if score_path.exists() else None
    replay_path=root/('wide-paired-summary.json' if wide else 'paired-summary.json')
    replay=json.loads(replay_path.read_text()) if replay_path.exists() else {}
    result=assess(json.loads((root/'public-frontier.json').read_text(encoding='utf-8-sig')),receipt,score,replay)
    result['candidate']='candidate-wide-v1' if wide else 'candidate-b3-cache-v1'
    (root/('wide-submission-status.json' if wide else 'submission-status.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    sys.exit(0 if result['status']=='READY_FOR_PACKAGING' else 1)
