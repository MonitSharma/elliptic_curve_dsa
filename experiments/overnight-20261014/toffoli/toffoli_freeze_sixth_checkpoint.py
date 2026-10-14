"""Freeze completed v7..v12 evidence; later active consumer prototypes excluded."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
NAMES=['README.md','adaptive-cleanup-report-v7.md','actual-adaptive-guards-v7.json',
       'toffoli_actual_adaptive_guards_v7.py','toffoli_actual_lean_cleanup_v7.rs',
       'minaux-interfaces-v8-description.json','minaux-interfaces-v8-summary.json',
       'toffoli_minaux_interfaces_v8.py','toffoli_minaux_job_v8.sh',
       'minaux-seedproducts-v9-description.json','minaux-seedproducts-v9-summary.json',
       'toffoli_minaux_seedproducts_v9.py','toffoli_minaux_seedproducts_job_v9.sh',
       'minimal-aux-constructor-report-v10.md','symplectic-interface-v10-description.json',
       'symplectic-interface-v10-summary.json','toffoli_symplectic_interface_v10.py',
       'toffoli_symplectic_search_v10.py','toffoli_symplectic_job_v10.sh','toffoli_minaux_archive_v10.py',
       'symplectic-family-v11-description.json','symplectic-family-v11-summary.json',
       'toffoli_symplectic_family_v11.py','toffoli_symplectic_family_job_v11.sh',
       'two-product-extension-v12-summary.json','toffoli_two_product_extension_v12.py','toffoli_two_product_job_v12.sh',
       'toffoli_freeze_sixth_checkpoint.py']

def main():
    raw=HERE.parents[2]/'research-output/overnight-20261014/toffoli/two-product-v12'
    receipt=json.loads((raw/'raw-receipt.json').read_bytes())
    assert receipt['status']=='unsat' and int((raw/'run.exit').read_text())==0
    receipt.update(pid=int((raw/'run.pid').read_text()),exit_code=0,
                   raw_evidence_directory='research-output/overnight-20261014/toffoli/two-product-v12',
                   evidence_sha256={name:hashlib.sha256((raw/name).read_bytes()).hexdigest()
                                    for name in ['raw-receipt.json','query.smt2','run.log','run.pid','run.exit','settings.txt','finished.txt']})
    (HERE/'two-product-extension-v12-summary.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    report={'status':'completed_v7_through_v12_frozen','root_parent_checkpoint':'9fd8dc4',
            'qualified_score':None,'active_jobs':[],
            'v7_status':'sourcealgebraonly_no_native_or_completecost',
            'v8_status':'89_selected_interfaces_closed_negative',
            'v9_status':'236_selected_interfaces_closed_negative',
            'v10_status':'exact3product_partialprefix_one_interface_closed_negative',
            'v11_status':'256_selected_interfaces_closed_negative',
            'v12_status':'trusted_parallel2product_UNSAT_no_formalcertificate',
            'hash_scope':'SHA256 of projected Git blob bytes with CRLF normalized to LF; raw evidence hashes in individual receipts remain raw-byte scope.',
            'files':{name:hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in NAMES},
            'excluded':'Active v13+ changed-consumer files and ignored raw evidence are not in this frozen set.'}
    (HERE/'sixth-checkpoint-receipt.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('frozen files:',len(NAMES))

if __name__=='__main__':main()
