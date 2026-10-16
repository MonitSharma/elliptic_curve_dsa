from pathlib import Path
import csv,json,multiprocessing as mp,time,sys
from importlib.machinery import SourceFileLoader
predict=SourceFileLoader('recovered_model',str(Path(__file__).parent/'predict-recovered.py')).load_module().predict
ROWS=[]

def worker(task):
    first,last,output=task
    counts=dict(shots=0,tp=0,fp=0,tn=0,fn=0,unknown=0,unknown_bad=0)
    with open(output,'w')as sink:
        for row in ROWS[first:last]:
            r=predict(row);truth=row['value']=='1';counts['shots']+=1
            if not r['clean_loan_model_supported']:
                counts['unknown']+=1;counts['unknown_bad']+=truth
            else:
                p=r['predicted_wrong_value'];counts['tp' if truth and p else 'fn' if truth else 'fp' if p else 'tn']+=1
            if truth or r['predicted_wrong_value'] or not r['clean_loan_model_supported']:
                sink.write(json.dumps(dict(batch=int(row['batch']),lane=int(row['lane']),value=int(truth),**r))+'\n')
    return counts

def main():
    global ROWS
    source,root=sys.argv[1:3];workers=int(sys.argv[3]);assert 1<=workers<=14
    root=Path(root);root.mkdir(exist_ok=True)
    with open(source)as inp:ROWS=list(csv.DictReader(inp,delimiter='\t'))
    # Linux fork shares the preserved immutable census population.
    tasks=[(len(ROWS)*i//workers,len(ROWS)*(i+1)//workers,str(root/f'part-{i:02d}.jsonl'))for i in range(workers)]
    start=time.perf_counter();total={}
    with mp.get_context('fork').Pool(workers)as pool:
        for counts in pool.imap_unordered(worker,tasks):
            for k,v in counts.items():total[k]=total.get(k,0)+v
            print(json.dumps(dict(total,seconds=time.perf_counter()-start)),flush=True)
    total.update(seconds=time.perf_counter()-start,workers=workers,source='4b2ec52f',population='preserved_tip-4b2ec52f_census_4096_batches',status='DIAGNOSTIC_ONLY_UNPROVED_PRIMITIVE_SUMMARIES_NO_REJECTION')
    (root/'summary.json').write_text(json.dumps(total,indent=2)+'\n')
    print(json.dumps(total),flush=True)

if __name__=='__main__':main()
