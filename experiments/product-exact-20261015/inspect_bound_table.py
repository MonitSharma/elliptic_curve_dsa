import collections,json,struct
from pathlib import Path
root=Path(__file__).resolve().parent
path=root/'tip/src/point_add/y42_bound.bin';data=path.read_bytes();assert data[:8]==b'Y42BOUND'
n,fp,ne=struct.unpack_from('<QQI',data,8);flat=28+12*ne;rows=(len(data)-flat)//12
styles=collections.Counter();edits=[]
for i in range(ne):
    at,start,count=struct.unpack_from('<III',data,28+12*i)
    kinds=tuple(struct.unpack_from('<6H',data,flat+12*j)[0] for j in range(start,start+count))
    styles[kinds]+=1;edits.append(at)
result={'input_ops':n,'edits':ne,'replacement_rows':rows,'first_edit':min(edits),'last_edit':max(edits),'replacement_style_counts':[{'kinds':list(k),'count':v} for k,v in styles.most_common()]}
(root/'bound-table-structure.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
