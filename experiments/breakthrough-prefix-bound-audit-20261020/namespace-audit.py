"""Classify mismatches, without applying or moving any rewrite."""
import collections,json,mmap,struct
from pathlib import Path
r=Path(__file__).resolve().parent;summary=json.loads((r/'CONTEXT-BINDING-AUDIT.json').read_text());source=r.parent/'breakthrough-prefix-tick-canonical-20261020';data=(source/'observer/src/point_add/square_finish.bin').read_bytes();ne=struct.unpack_from('<I',data)[0];counts=collections.Counter();delta_hist=collections.Counter();samples=[];index_hist=collections.Counter();no=(1<<64)-1;offsets=sorted({0,summary['record_index_delta'],summary['record_index_delta']-1,summary['record_index_delta']+1});maxclass={}
with(r/'control.records.bin').open('rb')as af,(r/'mixed.records.bin').open('rb')as bf:
 a=mmap.mmap(af.fileno(),0,access=mmap.ACCESS_READ);b=mmap.mmap(bf.fileno(),0,access=mmap.ACCESS_READ);nb=len(b)//56
 for label,values in [('control',a),('mixed',b)]:
  maximum=0
  for row in struct.iter_unpack('<7Q',values):
   for value in row[4:6]:
    if value!=no:maximum=max(maximum,value)
  maxclass[label]=maximum+1
 for e in range(ne):
  at=struct.unpack_from('<I',data,4+12*e)[0];old=struct.unpack_from('<7Q',a,at*56);matches=[]
  for d in offsets:
   j=at+d
   if not 0<=j<nb:continue
   new=struct.unpack_from('<7Q',b,j*56)
   if tuple(old[k]for k in[0,1,2,3,6])==tuple(new[k]for k in[0,1,2,3,6])and all((old[k]==no)==(new[k]==no)for k in[4,5]):matches.append((new!=old,sum(abs(new[k]-old[k])for k in[4,5]if old[k]!=no),abs(d),d,j,new))
  if not matches:counts['no_quantum_skeleton_match_at_tested_offsets']+=1;continue
  _,_,_,d,j,new=min(matches);index_hist[str(d)]+=1
  if old==new:counts['exact_record_at_tested_offset']+=1
  else:
   counts['quantum_skeleton_equal_only_classical_labels_differ']+=1
   for k in[4,5]:
    if old[k]!=no and old[k]!=new[k]:delta_hist[str((k,old[k],new[k],new[k]-old[k]))]+=1
   if len(samples)<20:samples.append({'old_index':at,'new_index':j,'offset':d,'old':old,'new':new})
 a.close();b.close()
result={'status':'CLASSICAL_NAMESPACE_MISMATCH_CLASSIFICATION_ONLY','table_edits':ne,'candidate_index_offsets':offsets,'counts':dict(counts),'matched_index_offset_histogram':dict(index_hist),'classical_bits_max_plus_one':maxclass,'label_changes':dict(delta_hist),'examples':samples,'scope':'Only a diagnostic of candidate alignments and field differences. No proof of unique mapping, no table edits, no binding change, no final gate or score. A whole-classical-namespace alpha-renaming is valid only when injective and respecting fixed input bits and every read/write; any proposed map needs independent exact full-record checks.'};(r/'NAMESPACE-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['label_changes','examples']},indent=2));print('Classical label pair kinds',len(delta_hist));(r/'namespace.exit').write_text('0\n')
