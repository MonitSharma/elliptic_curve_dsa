from pathlib import Path
from array import array
from bisect import bisect_right
from collections import Counter
import ctypes,ctypes.util,hashlib,json,struct,time
from primitive import check
from patterns import find_matches

R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((R/'DECLARATION.json').read_text());source=Path(d['source'])
before={name:sha(R/name)for name in ['DECLARATION.json','primitive.py','patterns.py','pattern-tests.py','scan.py','run.sh']}
assert sha(source)==d['source_sha256']
(R/'SOURCE-PINS-BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
proof=check();(R/'PRIMITIVE-TESTS.json').write_text(json.dumps(proof,indent=2)+'\n')
start=time.monotonic();blob=source.read_bytes();assert blob[:8]==b'QECCOPSZ'
n=struct.unpack_from('<Q',blob,8)[0];assert n==10522755
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
raw=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(raw,len(raw),blob[16:],len(blob)-16)==len(raw)
del blob
N=2**64-1
op=lambda i:struct.unpack_from('<7Q',raw,i*56)
positions={};barriers=array('I');ccx=array('I');input_bits=set()
pure={0,6,7,8,9,10,13,14}
for i in range(n):
 k,a,b,t,bt,c,rt=op(i)
 assert k<=17
 if k==2 and bt!=N:input_bits.add(bt)
 if k not in pure:barriers.append(i)
 for q in {a,b,t}-{N}:positions.setdefault(q,array('I')).append(i)
 if k==13:ccx.append(i)
print(json.dumps({'prepass_seconds':time.monotonic()-start,'ops':n,'CCX':len(ccx),'qubit_ids':len(positions),'barriers':len(barriers)}),flush=True)

digest_span=lambda i,end:hashlib.sha256(ctypes.string_at(ctypes.addressof(raw)+i*56,(end-i)*56)).hexdigest()
matches,first_two=find_matches(op,n,positions,barriers,ccx,digest_span)

# Conservative exact constant propagation for classical enables, preserving
# Push snapshots. Unknown inputs/MR never become a known constant by sampling.
states={b:2 for b in input_bits};base=1;stack=[];at={x['begin']:x for x in matches}
AND=lambda x,y:0 if x==0 or y==0 else 1 if x==y==1 else 2
for i in range(n):
 k,a,b,t,bt,c,rt=op(i);cond=AND(base,1 if c==N else states.get(c,0))
 if i in at:at[i].update(entry_depth=len(stack),provable_enable=['false','true','unknown'][cond])
 old=states.get(bt,0)
 if k==3:states[bt]=old if cond==0 else 1-old if cond==1 and old!=2 else 2
 elif k==4:states[bt]=0 if cond==1 or old==0 else old if cond==0 else 2
 elif k==5:states[bt]=1 if cond==1 or old==1 else old if cond==0 else 2
 elif k==12:states[bt]=old if cond==0 else 2
 elif k==15:stack.append(base);base=AND(base,states.get(c,0))
 elif k==16:assert stack; base=stack.pop()
assert not stack
matches.sort(key=lambda x:(x['begin'],x['end_exclusive'],x['a']))
selected=[];last=0
for match in matches:
 if match['begin']>=last:selected.append(match);last=match['end_exclusive']
summary=Counter(x['provable_enable']for x in selected)
assert sha(source)==d['source_sha256']
after={name:sha(R/name)for name in before};assert before==after
(R/'SOURCE-PINS-AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
report={'status':'SOURCE_ONLY_EXACT_MAJ_CONE_INVENTORY_COMPLETE','source_sha256':d['source_sha256'],'ops':n,
 'all_syntactic_matches':len(matches),'contiguous_matches':sum(x['contiguous']for x in matches),
 'disjoint_intervening_block_matches':sum(not x['contiguous']for x in matches),
 'first_CCX_CX_prefixes':first_two,'deterministic_nonoverlapping_selected':len(selected),
 'selected_provable_enable_counts':dict(summary),'guaranteed_executed_saving_T_per_shot':summary['true'],
 'maximum_syntactic_selected_saving_T_per_shot':summary['true']+summary['unknown'],
 'conditional_executed_mean_saving':'UNKNOWN; no packet/census simulated or sampled',
 'all_matches':matches,'selected_macro_indices':[x['macro_indices']for x in selected],
 'method':'Exact whole-stream four-gate projected pattern. Every intervening operation is pure quantum/global-phase on wires disjoint from all four macro wires; no classical write, Push/Pop, MR/reset, metadata or observation is crossed. Same direct condition plus unchanged scope snapshot gives one immutable classical enable. Greedy selection uses disjoint entire source spans.',
 'elapsed_seconds':time.monotonic()-start,'candidate_written':False,'census_or_nonce_search':False,'record_claim':False}
(R/'INVENTORY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in('all_matches','selected_macro_indices')}),flush=True)
