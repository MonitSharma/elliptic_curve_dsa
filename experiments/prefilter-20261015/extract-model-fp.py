from pathlib import Path
import csv,json
r=Path(__file__).parent
bad=[]
for p in (r/'evidence/recovered-population').glob('part-*.jsonl'):
 for s in p.read_text().splitlines():
  v=json.loads(s)
  if not v['value'] and v['predicted_wrong_value'] and v['clean_loan_model_supported']:bad.append(v)
assert len(bad)==4
keys={(x['batch'],x['lane'])for x in bad}
with (r/'evidence/census-coordinates4096.tsv').open()as f:
 inp=csv.DictReader(f,delimiter='\t');fields=inp.fieldnames;rows=[x for x in inp if (int(x['batch']),int(x['lane']))in keys]
with (r/'evidence/recovered-false-positives.tsv').open('w')as f:
 w=csv.DictWriter(f,fields,delimiter='\t');w.writeheader();w.writerows(rows)
(r/'evidence/recovered-false-positives.json').write_text(json.dumps(bad,indent=2)+'\n')
print(json.dumps(sorted(keys)))
