import ctypes,ctypes.util,hashlib,json,struct
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;BASE=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((R/'DECLARATION.json').read_text())
for name,h in d['pins'].items():assert sha(BASE/name)==h,name
inventory=json.loads((R/'provenance/ALL70.json').read_text());assert len(inventory)==70
byindex={x['actual_index']:x for x in inventory};assert len(byindex)==70
p=BASE/'product-exact-20261015/tip/ops.bin';b=p.read_bytes();assert b[:8]==b'QECCOPSZ'
n=struct.unpack_from('<Q',b,8)[0];assert n==11630716
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),b[16:],len(b)-16)==len(out)
N=2**64-1
def op(i):return struct.unpack_from('<7Q',out,i*56)
for i,x in byindex.items():assert list(op(i))==x['new'] and x['old'][0]==13 and x['new'][0]==8
active={};results=[];depth=0
def finish(target,reason,index,o):
 x=active.pop(target);x.update(status=reason,end_index=index,end_op=list(o),span_ops=index-x['begin_index']+1,
  span_sha256=hashlib.sha256(ctypes.string_at(ctypes.addressof(out)+x['begin_index']*56,(index-x['begin_index']+1)*56)).hexdigest())
 results.append(x)
for i in range(n):
 actual=op(i);k,a,c,t,bt,cc,rt=actual
 if k==16:depth-=1;assert depth>=0
 # All-restored operands are used in the scan too: an absent inherited control
 # must not hide a new value fanout introduced by another restoration.
 effective=tuple(byindex[i]['old']) if i in byindex else actual
 ek,ea,ec,et,eb,ee,er=effective
 for target in list(active):
  if ek in (0,1,2,3,4,5,15,16,17):continue
  if ek in (7,9,14):
   if target in (ea,ec,et):active[target]['phase_reads'].append(i)
   continue
  if target in (ea,ec):finish(target,'UNKNOWN_VALUE_CONTROL_OR_SWAP_FANOUT',i,effective);continue
  if et!=target:continue
  if ek in (6,8,13):
   active[target]['same_target_updates'].append(i);continue
  if ek in (11,12):
   if depth==0 and ee==N:
    # Protected HMR writes a fresh random classical word independently of q;
    # both R and HMR clear q and consume the same draw. Only phase may differ.
    finish(target,'UNIVERSAL_VALUE_CLASSICAL_INERT_HMR' if ek==12 else 'UNIVERSAL_VALUE_CLASSICAL_INERT_R_PROTECTED_SEMANTICS',i,effective)
   else:finish(target,'UNKNOWN_CONDITIONAL_RESET',i,effective)
   continue
  finish(target,'UNKNOWN_VALUE_TARGET_OPERATION',i,effective)
 if i in byindex:
  x=byindex[i];target=x['new'][3]
  if target in active:finish(target,'UNKNOWN_OVERLAPPING_CHANGED_TARGET',i,effective)
  active[target]={'row':x['row'],'begin_index':i,'target':target,'old':x['old'],'new':x['new'],
   'entry_depth':depth,'direct_condition':None if cc==N else cc,'phase_reads':[],'same_target_updates':[],
   'scan_both_old_and_restored_operand_sets':True,'actual_regions':x['actual_regions']}
 if k==15:depth+=1
assert depth==0
for target in list(active):finish(target,'UNKNOWN_LIVE_TO_END',n-1,op(n-1))
assert len(results)==70
results.sort(key=lambda x:x['row'])
for name,h in d['pins'].items():assert sha(BASE/name)==h,name
report={'status':'SOURCE_ONLY_UNIFORM_ALL70_CLASSIFICATION_NO_MASK_TRANSFER','source_sha256':sha(p),
 'summary':dict(Counter(x['status'] for x in results)),'sites':results,
 'theorem_scope':'Inert classification is exact arbitrary-entry quantum/classical value equivalence for a single restoration through the recorded reset, under identical fresh MR words and exact protected semantics. Phase may differ. Both actual/restored operand sets scanned, so another restored control cannot hide a fanout. UNKNOWN never grants transfer.',
 'authority':False}
(R/'CLASSIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary']),flush=True)
