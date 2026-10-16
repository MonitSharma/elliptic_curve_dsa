from pathlib import Path
import csv,json,time,sys
import walk_model as m

def predict(row):
    tx,ty,ox,oy,ex,ey=[int(row[k],16) for k in ('tx','ty','ox','oy','ex','ey')]
    div={};mul={}
    slope,_,_=m.walk((tx-ox)%m.P,leg='divide',payload=(ty-oy)%m.P,diagnostics=div)
    denominator=(div['recovered_denominator']+3*ox-slope*slope)%m.P
    product,_,_=m.walk(denominator,False,'multiply',payload=slope,diagnostics=mul)
    actualx=(ox-mul['recovered_denominator'])%m.P
    actualy=(product-oy)%m.P
    supported=div['endpoint_unit'] and mul['endpoint_unit'] and mul.get('FM_loan_clean',False)
    return dict(predicted_wrong_value=(actualx,actualy)!=(ex,ey),clean_loan_model_supported=supported,divide=div,multiply=mul)

def main():
    source,out=sys.argv[1:3]
    counts=dict(shots=0,tp=0,fp=0,tn=0,fn=0,unknown=0,unknown_bad=0)
    start=time.perf_counter()
    with open(source)as inp,open(out,'w')as sink:
        for row in csv.DictReader(inp,delimiter='\t'):
            r=predict(row);truth=row['value']=='1';counts['shots']+=1
            if not r['clean_loan_model_supported']:
                counts['unknown']+=1;counts['unknown_bad']+=truth
            else:
                p=r['predicted_wrong_value'];counts['tp' if truth and p else 'fn' if truth else 'fp' if p else 'tn']+=1
            if truth or r['predicted_wrong_value'] or not r['clean_loan_model_supported']:
                sink.write(json.dumps(dict(batch=int(row['batch']),lane=int(row['lane']),value=int(truth),**r))+'\n')
            if counts['shots']%4096==0:print(json.dumps(dict(counts,seconds=time.perf_counter()-start)),flush=True)
    counts.update(seconds=time.perf_counter()-start,status='DIAGNOSTIC_ONLY_UNPROVED_PRIMITIVE_SUMMARIES_NO_REJECTION')
    Path(out+'.summary.json').write_text(json.dumps(counts,indent=2)+'\n');print(json.dumps(counts),flush=True)

if __name__=='__main__':main()
