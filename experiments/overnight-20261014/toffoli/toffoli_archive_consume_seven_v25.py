"""Freeze exact low13 obligation/rank and selected closure negative."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE.parents[2]/'research-output/overnight-20261014/toffoli'
def main():
    names=['consume-seven-report-v25.md','toffoli_consume_seven_v24.py','toffoli_consume_seven_job_v24.sh',
           'toffoli_consume_seven_complete_v25.py','toffoli_consume_seven_complete_job_v25.sh','toffoli_archive_consume_seven_v25.py']
    netname='consume-seven-v24-netlist.json';shutil.copyfile(RAW/'consume-v24'/netname,HERE/netname);names.append(netname)
    for directory,summary in [('consume-v24','consume-seven-v24-summary.json'),('consume-v25','consume-seven-completion-v25-summary.json')]:
        folder=RAW/directory;report=json.loads((folder/'raw-receipt.json').read_bytes());assert int((folder/'run.exit').read_text())==0
        files=['raw-receipt.json','run.log','run.pid','run.exit','finished.txt','settings.txt']
        files+=[p.name for p in folder.glob('*.smt2')]
        report.update(pid=int((folder/'run.pid').read_text()),exit_code=0,raw_evidence_directory=str(folder.relative_to(HERE.parents[2])).replace('\\','/'),
                      evidence_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in files})
        (HERE/summary).write_bytes((json.dumps(report,indent=2)+'\n').encode());names.append(summary)
    manifest={'status':'completed_low13_value_contract_and_selected_closure_frozen','qualified_score':None,'active_jobs':[],
              'hash_scope':'SHA256 projected Git blob bytes with CRLF normalized to LF; raw evidence hashes preserve raw bytes.',
              'files':{name:hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in names},
              'dependency':'Frozen toffoli_cubic_factor_v23.py is bound by cubic-producer-v23-checkpoint-receipt.json; fast loader and closure helpers bound by earlier checkpoints.',
              'limits':'Complete primitive value obligations only, with selected rank-minimum closure negative; no native phase/cleanup or circuit score.'}
    (HERE/'consume-seven-v25-checkpoint-receipt.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print(f'frozen{len(names)}files plusmanifest')
if __name__=='__main__':main()
