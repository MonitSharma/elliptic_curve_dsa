"""Freeze exact absorbed-consumer contract with cost-negative status."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE.parents[2]/'research-output/overnight-20261014/toffoli/absorb-v26'
def main():
    names=['carry-absorb-report-v26.md','toffoli_carry_absorb_v26.py','toffoli_carry_absorb_job_v26.sh','toffoli_archive_absorb_v26.py']
    report=json.loads((RAW/'raw-receipt.json').read_bytes());assert int((RAW/'run.exit').read_text())==0
    assert report['arithmetic_mismatches']==0 and report['direct_AND_delta']==7
    files=['raw-receipt.json','run.log','run.pid','run.exit','finished.txt','settings.txt','absorb-v26-netlist.json']
    report.update(pid=int((RAW/'run.pid').read_text()),exit_code=0,route_status='closed_cost_negative_without_resynthesis',
                  raw_evidence_directory=str(RAW.relative_to(HERE.parents[2])).replace('\\','/'),
                  evidence_sha256={name:hashlib.sha256((RAW/name).read_bytes()).hexdigest() for name in files})
    summary='carry-absorb-v26-summary.json';(HERE/summary).write_bytes((json.dumps(report,indent=2)+'\n').encode());names.append(summary)
    netname='carry-absorb-v26-netlist.json';shutil.copyfile(RAW/'absorb-v26-netlist.json',HERE/netname);names.append(netname)
    manifest={'status':'completed_exact_absorbed_contract_cost_negative_frozen','qualified_score':None,'active_jobs':[],
              'hash_scope':'SHA256 projected Git blob bytes with CRLF normalized to LF; raw evidence hashes preserve raw bytes.',
              'files':{name:hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in names},
              'dependency':'Frozen consume-seven-v24-netlist.json and earlier fast loader/helpers.',
              'limits':'Primitive nonlinear value contract only; direct45 versus38 ANDs is costnegative, no quantum phase or whole circuit qualification.'}
    (HERE/'carry-absorb-v26-checkpoint-receipt.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print(f'frozen{len(names)}files plusmanifest')
if __name__=='__main__':main()
