from pathlib import Path
import csv,json
root=Path(__file__).parent
misses={(r['batch'],r['lane']) for r in map(json.loads,(root/'evidence/native-walk4096.jsonl').read_text().splitlines()) if r['value']==1 and not r['predicted_wrong_value']}
with open(root/'evidence/census-coordinates4096.tsv') as inp:
    reader=csv.DictReader(inp,delimiter='\t');fields=reader.fieldnames
    with open(root/'evidence/fold-selected.tsv','w',newline='') as selected,open(root/'evidence/unmodeled55.tsv','w',newline='') as unmodeled:
        output=csv.DictWriter(selected,fieldnames=fields,delimiter='\t');output.writeheader()
        missing=csv.DictWriter(unmodeled,fieldnames=fields,delimiter='\t');missing.writeheader()
        for i,row in enumerate(reader):
            if row['value']=='1' or i<4096:output.writerow(row)
            if (int(row['batch']),int(row['lane'])) in misses:missing.writerow(row)
print('Preserved55unmodeledvaluefailures andall431valuefailures+earlycontrols')
