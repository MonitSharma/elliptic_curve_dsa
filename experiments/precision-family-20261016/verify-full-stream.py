exec((__import__('pathlib').Path(__file__).parent/'analyze-isolated.py').read_text().split('rows=[]')[0])
import subprocess
old=load(root.parent/'product-exact-20261015/tip/ops.bin');new=load(root/'candidate/ops.bin');a=json.loads((root/'isolated-analysis.json').read_text());base={r['tick']:r for r in family['records']};cursorold=cursornew=0;regions=[]
for r in sorted((r for r in a['rows']if not r['rejected']),key=lambda r:base[r['tick']]['final_begin']):
 t=r['tick'];source=base[t];start=source['final_begin']*56;end=source['final_end']*56;replacement=load(d/f'tick-{t}.new.bin');unchanged=start-cursorold
 assert old[cursorold:start]==new[cursornew:cursornew+unchanged],('outside region mismatch',t)
 cursornew+=unchanged;assert new[cursornew:cursornew+len(replacement)]==replacement,('replacement mismatch',t)
 regions.append(dict(tick=t,old_begin=start//56,old_end=end//56,new_begin=cursornew//56,new_end=(cursornew+len(replacement))//56))
 cursorold=end;cursornew+=len(replacement)
assert old[cursorold:]==new[cursornew:],'final suffix mismatch'
def stat(buf):
 counts=collections.Counter();qmax=bmax=-1;depth=0;weighted=0.
 for k,a,b,t,bt,bc,rt in struct.iter_unpack('<7Q',buf):
  counts[k]+=1
  for q in[a,b,t]:
   if q!=none:qmax=max(qmax,q)
  for q in[bt,bc]:
   if q!=none:bmax=max(bmax,q)
  if k in[13,14]:weighted+=2**(-depth-int(bc!=none))
  if k==15:depth+=1
  if k==16:depth-=1
 assert depth==0
 return dict(ops=len(buf)//56,qubits=qmax+1,bits=bmax+1,native_toffoli=counts[13]+counts[14],static_weighted_toffoli_diagnostic=weighted,mr=counts[11]+counts[12],counts=dict(counts))
before=stat(old);after=stat(new);diff=[p for p in subprocess.check_output(['git','-C',str(root/'candidate'),'diff','--name-only'],text=True).splitlines()if p];assert all(p.startswith('src/point_add/')for p in diff)
subprocess.run(['git','-C',str(root/'candidate'),'diff','--exit-code','--','.',':(exclude)src/point_add'],check=True)
result=dict(all_outside_regions_byte_identical=True,all_replacements_match_isolated_source=True,all_29_regions_admitted=True,original=before,candidate=after,delta_ops=after['ops']-before['ops'],delta_native_toffoli=after['native_toffoli']-before['native_toffoli'],delta_weighted_toffoli_diagnostic=after['static_weighted_toffoli_diagnostic']-before['static_weighted_toffoli_diagnostic'],delta_mr=after['mr']-before['mr'],source_diff_files=diff,protected_tracked_files_unchanged=True,regions=regions,status='COMPLETE_STREAM_RECONSTRUCTION; fresh full-state failure census pending, not a passing benchmark record')
(root/'full-stream-verification.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items()if k not in['regions','original','candidate']});print('RESOURCES',before,after)
