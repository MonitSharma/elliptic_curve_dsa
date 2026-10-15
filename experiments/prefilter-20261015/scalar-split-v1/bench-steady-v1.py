from pathlib import Path
import ctypes as c,time,json,hashlib,statistics,os
r=Path(__file__).parent;oldroot=r.parents[1]/'scalar-fast-20261015'
core=max(os.sched_getaffinity(0));os.sched_setaffinity(0,{core})
new=c.CDLL(str(r/'libscalar_split.so'));old=c.CDLL(str(oldroot/'libscalar_fast_batch.so'))
for dll in[new,old]:
 dll.scalar_fast_fixed_init.argtypes=[c.c_uint];dll.scalar_fast_fixed_init.restype=c.c_int
 dll.scalar_fast_pairs.argtypes=[c.c_uint,c.c_void_p,c.c_void_p];dll.scalar_fast_pairs.restype=c.c_int
 assert dll.scalar_fast_fixed_init(20)==1
new.scalar_fast_inputs.argtypes=[c.c_uint,c.c_void_p,c.c_void_p];new.scalar_fast_inputs.restype=c.c_int
fn=dict(old_full=old.scalar_fast_pairs,new_full=new.scalar_fast_pairs,inputs=new.scalar_fast_inputs);out=c.create_string_buffer(64*192);records=[];shots=131072
for trial in range(9):
 raw=hashlib.shake_256(b'scalar-split-steady-v1'+trial.to_bytes(4,'little')).digest(shots*64);src=c.create_string_buffer(raw);base=c.addressof(src);modes=['old_full','new_full','inputs'];shift=trial%3;order=modes[shift:]+modes[:shift]
 row=dict(trial=trial,shots=shots,order=order)
 for mode in order:
  st=time.monotonic();f=fn[mode]
  for at in range(0,shots,64):assert f(64,base+at*64,out)==1
  row[mode+'_s']=time.monotonic()-st
 row['inputs_vs_original']=row['inputs_s']/row['old_full_s'];row['inputs_vs_same_library_full']=row['inputs_s']/row['new_full_s'];row['same_library_vs_original_full']=row['new_full_s']/row['old_full_s'];records.append(row);print(json.dumps(row),flush=True)
result=dict(status='PINNED_SINGLE_CORE_FRESH_SCALAR_API_TIMING_ONLY',affinity_core=core,window=20,rounds=len(records),fresh_unique_pairs_per_round=shots,total_unique_pairs=shots*len(records),median_us={mode:statistics.median(v[mode+'_s']*1e6/shots for v in records)for mode in modes},median_paired_ratio={name:statistics.median(v[name]for v in records)for name in['inputs_vs_original','inputs_vs_same_library_full','same_library_vs_original_full']},all_records=records,source_sha256=hashlib.sha256((r/'scalar_split.c').read_bytes()).hexdigest(),library_sha256=hashlib.sha256((r/'libscalar_split.so').read_bytes()).hexdigest(),original_library_sha256=hashlib.sha256((oldroot/'libscalar_fast_batch.so').read_bytes()).hexdigest(),not_claimed=['pipelineintegration','nonce throughputgain'])
(r/'steady-benchmark-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='all_records'}))
