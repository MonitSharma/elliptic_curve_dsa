"""Freeze all completed post25 proofs/failures and final track status."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE.parents[2]/'research-output/overnight-20261014/toffoli'
def main():
    names=['consumer-cleanup-report-v29.md','consumer-cleanup-cost-v29.json','final-track-report.md',
           'toffoli_consumer_cleanup_v27.py','toffoli_consumer_cleanup_job_v27.sh',
           'toffoli_consumer_cleanup_v27r1.py','toffoli_consumer_cleanup_job_v27r1.sh',
           'toffoli_consumer_cleanup_dag_v28.py','toffoli_consumer_cleanup_dag_job_v28.sh',
           'toffoli_cleanup_cost_v29.py','toffoli_archive_final_v29.py']
    for directory,summary in [('cleanup-v27r1','consumer-cleanup-v27r1-summary.json'),
                              ('cleanup-v28','consumer-cleanup-v28-summary.json')]:
        folder=RAW/directory;report=json.loads((folder/'raw-receipt.json').read_bytes());assert int((folder/'run.exit').read_text())==0
        files=['raw-receipt.json','run.log','run.pid','run.exit','finished.txt','settings.txt']
        report.update(pid=int((folder/'run.pid').read_text()),exit_code=0,
                      raw_evidence_directory=str(folder.relative_to(HERE.parents[2])).replace('\\','/'),
                      evidence_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in files})
        (HERE/summary).write_bytes((json.dumps(report,indent=2)+'\n').encode());names.append(summary)
    failed=RAW/'cleanup-v27-failed';assert int((failed/'run.exit').read_text())==1
    failure={'status':'preserved_failed_unverified_seed_rank_assertion','pid':int((failed/'run.pid').read_text()),'exit_code':1,
             'wrong_assumption':'12retained fields were independent relativepostraw; actualrank11, seed26 not27',
             'phase_or_native_work_performed':False,'qualified_score':None,
             'raw_evidence_directory':str(failed.relative_to(HERE.parents[2])).replace('\\','/'),
             'evidence_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(failed.iterdir()) if p.is_file()}}
    fn='consumer-cleanup-v27-failure.json';(HERE/fn).write_bytes((json.dumps(failure,indent=2)+'\n').encode());names.append(fn)
    inherited=json.loads((HERE/'carry-absorb-v26-checkpoint-receipt.json').read_bytes())
    names+=list(inherited['files'])+['carry-absorb-v26-checkpoint-receipt.json']
    manifest={'status':'completed_final_toffoli_track_frozen_no_original_qualified_record','qualified_score':None,'active_jobs':[],
              'hash_scope':'SHA256 projected Git blob bytes with CRLF normalized to LF; raw evidence hashes preserve raw bytes.',
              'files':{name:hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in names},
              'dependencies':'Checkpoints throughV25 preserved; v29context/source hashes bind existing independent product trace and baseline planner.',
              'limits':'No full original point-addition improvement; positive components and selected negative interfaces/plans are individually scoped.'}
    (HERE/'final-track-checkpoint-receipt.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print(f'frozen{len(names)}files plusmanifest')
if __name__=='__main__':main()
