# Separate refinement of the seven strict scanner SWAP stops. V1 is immutable.
import ctypes,ctypes.util,hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parent;B=R.parent;N=2**64-1
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((R/'DECLARATION.json').read_text())
for p,h in d['pins'].items():assert sha(B/p)==h
prior=json.loads((R/'CLASSIFICATION.json').read_text());inv=json.loads((R/'provenance/ALL70.json').read_text());sites={x['actual_index']:x for x in inv}
p=B/'product-exact-20261015/tip/ops.bin';b=p.read_bytes();n=struct.unpack_from('<Q',b,8)[0]
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),b[16:],len(b)-16)==len(out)
def op(i):return tuple(sites[i]['old'])if i in sites else struct.unpack_from('<7Q',out,i*56)
reports=[]
for row in prior['sites']:
 if row['status']!='UNKNOWN_VALUE_TARGET_OPERATION':continue
 assert row['end_op'][0]==10
 wire=row['target'];depth=row['entry_depth'];swaps=[];phase=[];status='UNKNOWN_LIVE_TO_END'
 for i in range(row['begin_index']+1,n):
  o=op(i);k,a,c,t,bt,cc,rt=o
  if k==16:depth-=1;assert depth>=0
  if k==15:depth+=1;continue
  if k in(0,1,2,3,4,5,16,17):continue
  if k in(7,9,14):
   if wire in(a,c,t):phase.append(i)
   continue
  if k==10 and wire in(c,t):
   if depth or cc!=N:status='UNKNOWN_CONDITIONAL_SWAP';break
   dest=t if wire==c else c;swaps.append([i,wire,dest]);wire=dest;continue
  if wire in(a,c):status='UNKNOWN_VALUE_CONTROL_FANOUT_AFTER_SWAP';break
  if t!=wire:continue
  if k in(6,8,13):continue
  if k in(11,12):status='UNIVERSAL_VALUE_CLASSICAL_INERT_AFTER_EXACT_SWAP'if depth==0 and cc==N else'UNKNOWN_CONDITIONAL_RESET';break
  status='UNKNOWN_TARGET_OPERATION';break
 reports.append({'row':row['row'],'begin_index':row['begin_index'],'status':status,'end_index':i,'end_op':list(o),'tracked_wire':wire,'swaps':swaps,'phase_reads':phase})
assert len(reports)==7
for p,h in d['pins'].items():assert sha(B/p)==h
result={'status':'SOURCE_ONLY_SWAP_REFINEMENT','authority':False,'reports':reports}
(R/'SWAP-REFINEMENT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
