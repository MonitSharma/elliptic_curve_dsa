"""Freeze completed v17/v18 targeted carry relations and completion receipts."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE.parents[2]/'research-output/overnight-20261014/toffoli'
NAMES=['consume-next-carry-v17-description.json','consume-next-carry-v17-netlist.json','consume-next-carry-v17-summary.json',
       'toffoli_consume_next_carry_v17.py','toffoli_consume_complete_v17.py','toffoli_consume_joint_job_v17.sh',
       'consume-relation-v18-description.json','consume-relation-v18-netlist.json','consume-relation-v18-summary.json',
       'toffoli_consume_relation_v18.py','toffoli_consume_complete_v18.py','toffoli_consume_joint_job_v18.sh',
       'consumer-carry-relations-report-v18.md','toffoli_archive_consumer_v18.py']

def main():
    for version,folder,name in [(17,'consume-next-v17','consume-next-carry-v17-summary.json'),(18,'consume-relation-v18','consume-relation-v18-summary.json')]:
        directory=RAW/folder;source=json.loads((directory/'raw-receipt.json').read_bytes())
        assert int((directory/'run.exit').read_text())==0
        report={key:value for key,value in source.items() if key!='steps'}
        report.update(pid=int((directory/'run.pid').read_text()),exit_code=0,
                      raw_evidence_directory=str(directory.relative_to(HERE.parents[2])).replace('\\','/'),
                      evidence_sha256={name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in ['raw-receipt.json','run.log','run.pid','run.exit','settings.txt','finished.txt']},
                      terminal_closure=source['steps'][-1]['closure'],terminal_factor=source['steps'][-1].get('factor'))
        if version==18:
            preliminary=RAW/'consume-relation-v18-preliminary'
            report['preliminary_rank10_description_sha256']=hashlib.sha256((preliminary/'description.json').read_bytes()).hexdigest()
            report['preliminary_source_sha256']=hashlib.sha256((preliminary/'source.py').read_bytes()).hexdigest()
            report['preliminary_scope']='Earlier single-known-relation greedy reduction also reached rank10. Frozen final source additionally tests all pairs of known-basis toggles without lower rank; neither proves minimum.'
        (HERE/name).write_bytes((json.dumps(report,indent=2)+'\n').encode())
    manifest={'status':'completed_v17_v18_frozen','active_jobs':[],'qualified_score':None,
              'hash_scope':'SHA256 projected Git blob bytes, CRLF normalized to LF; raw receipts retain raw-byte scope.',
              'files':{name:hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in NAMES},
              'excluded':'Active v19 sequential-escape query and later files.'}
    (HERE/'consumer-carry-v18-checkpoint-receipt.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print('frozen14files plusmanifest')

if __name__=='__main__':main()
