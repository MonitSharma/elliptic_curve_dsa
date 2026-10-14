"""Freeze completed cubic/source-producer/scalar probes without score claims."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE.parents[2]/'research-output/overnight-20261014/toffoli'
def main():
    names=['cubic-producer-report-v23.md','cubic-extension-v20-description.json','toffoli_cubic_extension_v20.py',
           'producer-range-v21-description.json','producer-escape-v21-equations.json',
           'toffoli_producer_range_v21.py','toffoli_producer_escape_prepare_v21.py','toffoli_producer_escape_solve_v21.py',
           'toffoli_producer_escape_audit_v21.py','toffoli_producer_escape_job_v21.sh',
           'scalar-three-v22-description.json','toffoli_scalar_three_v22.py','toffoli_scalar_three_job_v22.sh',
           'toffoli_cubic_complete_v23.py','toffoli_cubic_factor_v23.py','toffoli_cubic_job_v23.sh',
           'toffoli_archive_cubic_v23.py']
    for directory,summary,extra in [('producer-v21','producer-escape-v21-summary.json',['audit-receipt.json']),
                                     ('scalar-v22','scalar-three-v22-summary.json',[]),
                                     ('cubic-v23','cubic-completion-v23-summary.json',['factor-netlist.json'])]:
        folder=RAW/directory;report=json.loads((folder/'raw-receipt.json').read_bytes())
        assert int((folder/'run.exit').read_text())==0
        files=['raw-receipt.json','run.log','run.pid','run.exit','finished.txt','settings.txt']+extra
        files+=[p.name for p in folder.glob('*.smt2')]
        report.update(pid=int((folder/'run.pid').read_text()),exit_code=0,raw_evidence_directory=str(folder.relative_to(HERE.parents[2])).replace('\\','/'),
                      evidence_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in files})
        (HERE/summary).write_bytes((json.dumps(report,indent=2)+'\n').encode());names.append(summary)
        if extra==['audit-receipt.json']:
            audit=json.loads((folder/extra[0]).read_bytes());audit.update(pid=report['pid'],exit_code=0,raw_evidence_directory=report['raw_evidence_directory'])
            fn='producer-escape-v21-audit-summary.json';(HERE/fn).write_bytes((json.dumps(audit,indent=2)+'\n').encode());names.append(fn)
    manifest={'status':'completed_selected_cubic_and_arithmetic_domain_probes_frozen','qualified_score':None,'active_jobs':[],
              'hash_scope':'SHA256 projected Git blob bytes with CRLF normalized to LF; raw evidence hashes preserve raw bytes.',
              'files':{name:hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in names},
              'limits':'No complete constructor or original circuit qualification; scalar/interface/domain negatives only.',
              'excluded':'Later v24+ consumer-obligation hypotheses and ignored raw queries/logs.'}
    (HERE/'cubic-producer-v23-checkpoint-receipt.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print(f'frozen{len(names)}files plusmanifest')
if __name__=='__main__':main()
