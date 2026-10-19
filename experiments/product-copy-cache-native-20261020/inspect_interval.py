import json
from pathlib import Path
import inspect_stream as s
r=Path(__file__).resolve().parent;first,last=14241681,14245297;tracked={258,724,215,558};writes={q:[] for q in tracked};last_before={}
def changed(row):
    if row[0] in [6,8,11,12,13]:return [row[3]]
    if row[0]==10:return [row[2],row[3]]
    return []
depth=0;depths={};anchors={first,last}
for i in range(first,last):
    row=s.fields(i)
    for q in changed(row):
        if q in tracked:writes[q].append({'op':i,'fields':row})
for i in range(last-1,-1,-1):
    row=s.fields(i)
    for q in changed(row):
        if q in tracked and q not in last_before:last_before[q]={'op':i,'fields':row}
    if len(last_before)==len(tracked):break
anchors.update(x['op'] for x in last_before.values())
for i in range(last+1):
    row=s.fields(i)
    if i in anchors:depths[i]=depth
    if row[0]==15:depth+=1
    elif row[0]==16:depth-=1
    assert depth>=0
result={'status':'READ_ONLY_CLOSED_INTERVAL_AND_LAST_WRITER_INSPECTION','first':first,'last':last,'writes_including_first_excluding_last':writes,'last_writer_before_consume':last_before,'scope_depths':depths,'scope':'Structural diagnostic only. The final source certificate still needs independent source-bound zero/equality proofs.'}
(r/'INTERVAL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
