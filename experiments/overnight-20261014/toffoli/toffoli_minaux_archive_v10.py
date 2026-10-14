"""Archive compact source-bound receipts for completed v8/v9/v10 probes."""
import collections,hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RAW=ROOT/'research-output/overnight-20261014/toffoli'

def main():
    for version,folder,outname in [
        (8,'minaux-v8','minaux-interfaces-v8-summary.json'),
        (9,'minaux-v9','minaux-seedproducts-v9-summary.json'),
        (10,'symplectic-v10','symplectic-interface-v10-summary.json'),
        (11,'symplectic-v11','symplectic-family-v11-summary.json')]:
        directory=RAW/folder;source=json.loads((directory/'raw-receipt.json').read_bytes())
        assert int((directory/'run.exit').read_text())==0
        rows=source.get('examined',[])
        result={key:value for key,value in source.items() if key not in ['examined','interfaces','steps']}
        result.update(raw_evidence_directory=str(directory.relative_to(ROOT)).replace('\\','/'),
                      evidence_sha256={name:hashlib.sha256((directory/name).read_bytes()).hexdigest()
                                       for name in ['raw-receipt.json','run.log','run.pid','run.exit','settings.txt','finished.txt']},
                      pid=int((directory/'run.pid').read_text()),exit_code=0,
                      formal_proof_certificate_saved=False,qualified_score=None)
        if rows:
            result.update(examined_count=len(rows),status_counts=dict(collections.Counter(row['status'] for row in rows)),
                          final_AND_counts=dict(collections.Counter(str(row['final_ANDs']) for row in rows)))
            if version==9:
                result['constructed_operand_cosets']=sum(row['uses_constructed_basis_operand'] for row in source['interfaces'])
        else:
            result['terminal_current_span_rank']=source['steps'][-1]['closure']['stages'][-1]['current_span_rank']
            result['terminal_factor']=source['steps'][-1].get('factor')
        (HERE/outname).write_bytes((json.dumps(result,indent=2)+'\n').encode())
        print(outname,result['status'])

if __name__=='__main__':main()
