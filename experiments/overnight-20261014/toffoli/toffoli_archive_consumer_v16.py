"""Freeze completed changed-consumer v13..v16 evidence."""
import collections,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE.parents[2]/'research-output/overnight-20261014/toffoli'
NAMES=['consume-four-analysis-v13.json','consume-four-netlist-v13.json','toffoli_consume_four_contract_v13.py',
       'consume-four-aux-v14-description.json','consume-four-aux-v14-summary.json','toffoli_consume_four_aux_v14.py','toffoli_consume_four_job_v14.sh',
       'consume-four-subspaces-v15-description.json','consume-four-subspaces-v15-summary.json','toffoli_consume_four_subspaces_v15.py','toffoli_consume_four_subspaces_job_v15.sh',
       'consume-four-carry-pair-v16-description.json','consume-four-carry-pair-v16-netlist.json','consume-four-carry-pair-v16-preparation-failure.md',
       'consume-four-carry-pair-v16-summary.json','toffoli_consume_four_carry_pair_v16.py','toffoli_consume_four_complete_v16.py','toffoli_consume_four_joint_job_v16.sh',
       'consumer-fusion-report-v16.md','toffoli_archive_consumer_v16.py']

def main():
    for version,name in [(14,'consume-four-aux-v14-summary.json'),(15,'consume-four-subspaces-v15-summary.json'),(16,'consume-four-carry-pair-v16-summary.json')]:
        directory=RAW/f'consume-four-v{version}';source=json.loads((directory/'raw-receipt.json').read_bytes())
        assert int((directory/'run.exit').read_text())==0
        report={key:value for key,value in source.items() if key not in ['interfaces','examined','steps']}
        rows=source.get('examined',[])
        report.update(raw_evidence_directory=str(directory.relative_to(HERE.parents[2])).replace('\\','/'),
                      evidence_sha256={name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in ['raw-receipt.json','run.log','run.pid','run.exit','settings.txt','finished.txt']},
                      pid=int((directory/'run.pid').read_text()),exit_code=0,formal_proof_certificate_saved=False,qualified_score=None)
        if rows:
            report.update(examined_count=len(rows),status_counts=dict(collections.Counter(row['status'] for row in rows)),
                          final_AND_counts=dict(collections.Counter(str(row['final_ANDs']) for row in rows)))
        else:
            report['terminal_factor']=source['steps'][-1].get('factor')
            report['terminal_span_rank']=source['steps'][-1]['closure']['stages'][-1]['current_span_rank']
        (HERE/name).write_bytes((json.dumps(report,indent=2)+'\n').encode())
        print(name,report.get('status_counts',report['status']))
    manifest={'status':'completed_changed_consumer_v13_through_v16_frozen','qualified_score':None,'active_jobs':[],
              'hash_scope':'SHA256 projected Git blob bytes, CRLF normalized to LF. Raw receipts preserve raw byte hashes separately.',
              'files':{name:hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in NAMES},
              'excluded':'v17+ guided extensions are outside this completed set.'}
    (HERE/'consumer-fusion-v16-checkpoint-receipt.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())

if __name__=='__main__':main()
