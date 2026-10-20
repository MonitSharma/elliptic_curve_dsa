"""Find exact local contexts and classify old table edits; never apply them."""
import collections,json,mmap,struct
from pathlib import Path
r=Path(__file__).resolve().parent;s=json.loads((r/'CONTEXT-BINDING-AUDIT.json').read_text());source=r.parent/'breakthrough-prefix-tick-canonical-20261020';data=(source/'observer/src/point_add/square_finish.bin').read_bytes();ne=struct.unpack_from('<I',data)[0];flat=4+12*ne;delta=s['record_index_delta'];k=8;band=128;no=(1<<64)-1;mapping=[];unmapped=[];stats=collections.Counter();kinds=collections.Counter();bins=collections.Counter();shift_hist=collections.Counter()
with(r/'control.records.bin').open('rb')as af,(r/'mixed.records.bin').open('rb')as bf:
 a=mmap.mmap(af.fileno(),0,access=mmap.ACCESS_READ);b=mmap.mmap(bf.fileno(),0,access=mmap.ACCESS_READ);na=len(a)//56;nb=len(b)//56
 for e in range(ne):
  at,first,n=struct.unpack_from('<III',data,4+12*e);old=struct.unpack_from('<7Q',a,at*56);replacements=[tuple(no if x==65535 else x for x in struct.unpack_from('<6H',data,flat+12*j))+(no,)for j in range(first+1,first+n)];kinds[str((old[0],tuple(x[0]for x in replacements)))]+=1;bins[str(at//1000000)]+=1
  if len(replacements)==1:
   new=replacements[0]
   if new==old:stats['table_identity_row']+=1
   elif tuple(new[j]for j in[0,1,2,3,6])==tuple(old[j]for j in[0,1,2,3,6]):stats['table_single_row_only_classical_labels_change']+=1
   else:stats['table_single_row_other_change']+=1
  elif not replacements:stats['table_deletion']+=1
  else:stats['table_multirow_replacement']+=1
  lo=max(0,at-k);hi=min(na,at+k+1);needle=a[lo*56:hi*56];candidates=set()
  for center in[at,at+delta]:
   start=max(0,center-band-(at-lo));stop=min(nb,center+band+(hi-at));position=b.find(needle,start*56,stop*56)
   while position>=0:
    if position%56==0:candidates.add(position//56+(at-lo))
    position=b.find(needle,position+1,stop*56)
  if len(candidates)==1:
   position=next(iter(candidates));mapping.append([e,at,position]);shift_hist[str(position-at)]+=1
  else:unmapped.append({'edit':e,'old_index':at,'window_hits':sorted(candidates),'old_kind':old[0],'replacement_kinds':[x[0]for x in replacements]})
 a.close();b.close()
ordered=all(x[2]<y[2]for x,y in zip(mapping,mapping[1:]));result={'status':'EXACT_CONTEXT_WINDOW_DIAGNOSTIC_NO_TRANSPORT','window_radius_records':k,'search_band_records':band,'mapped_count':len(mapping),'unmapped_count':len(unmapped),'mapped_positions_strictly_ordered':ordered,'mapped_edits':mapping,'unmapped_edits':unmapped,'table_edit_shapes':dict(stats),'old_edit_million_index_histogram':dict(bins),'table_kind_pattern_counts':dict(kinds),'context_shift_histogram':dict(shift_hist),'scope':'Each reported window match is exact17-record content, unique only within tested positional bands, NOT globally certified. No rewrites applied or bindings changed. Missing contexts and transaction semantics must be resolved before any table transport. No final gate, nonce or scored result.'};(r/'WINDOW-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['mapped_edits','unmapped_edits','table_kind_pattern_counts']},indent=2));(r/'window.exit').write_text('0\n')
