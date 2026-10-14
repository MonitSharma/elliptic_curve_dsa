"""Freeze exact sequential escape query, encoding audit and scoped27AND proof."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE.parents[2]/'research-output/overnight-20261014/toffoli/sequential-v19'
NAMES=['sequential-escape-v19-description.json','sequential-escape-v19-summary.json','sequential-escape-v19-audit-summary.json',
       'sequential-escape-lower-bound-v19.md','toffoli_sequential_escape_prepare_v19.py','toffoli_sequential_escape_solve_v19.py',
       'toffoli_sequential_escape_job_v19.sh','toffoli_sequential_escape_audit_v19.py','toffoli_sequential_audit_job_v19.sh',
       'toffoli_archive_sequential_v19.py']

def main():
    solver=json.loads((RAW/'raw-receipt.json').read_bytes());audit=json.loads((RAW/'audit-receipt.json').read_bytes())
    assert solver['status']=='unsat' and int((RAW/'run.exit').read_text())==0
    assert audit['status']=='parsed_SMT_exact_ANF_and_independent_truth_ranks_verified' and int((RAW/'audit.exit').read_text())==0
    for report,filename,prefix,receipt in [(solver,'sequential-escape-v19-summary.json','run','raw-receipt.json'),
                                          (audit,'sequential-escape-v19-audit-summary.json','audit','audit-receipt.json')]:
        files=[receipt,'query.smt2',f'{prefix}.log',f'{prefix}.pid',f'{prefix}.exit']
        files+=['settings.txt','finished.txt'] if prefix=='run' else ['audit.settings.txt','audit.finished.txt']
        report.update(pid=int((RAW/f'{prefix}.pid').read_text()),exit_code=0,
                      raw_evidence_directory='research-output/overnight-20261014/toffoli/sequential-v19',
                      evidence_sha256={name:hashlib.sha256((RAW/name).read_bytes()).hexdigest() for name in files})
        (HERE/filename).write_bytes((json.dumps(report,indent=2)+'\n').encode())
    manifest={'status':'completed_scoped27AND_value_lower_bound_frozen','qualified_score':None,'active_jobs':[],
              'lower_bound_scope':'Fixed all14-input specified28-output straight-line XOR/AND value contract; trusted solver UNSAT without formal certificate.',
              'hash_scope':'SHA256 projected Git blob bytes with CRLF normalized to LF; raw evidence receipts use raw-byte hashes.',
              'files':{name:hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in NAMES},
              'excluded':'Later v20+ hypotheses and ignored raw SMT/log files.'}
    (HERE/'sequential-v19-checkpoint-receipt.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print('frozen10files plusmanifest')

if __name__=='__main__':main()
