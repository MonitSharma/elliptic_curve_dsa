from pathlib import Path
import ctypes,ctypes.util,struct,hashlib,json,collections,sys,time
from fractions import Fraction
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016');N=2**64-1
sys.path.insert(0,str(r.parent/'quantum-borrow-family-20261016'))
from classical_guards import ClassicalGuards,tests
sys.setrecursionlimit(20000)
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();assert d[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',d,8)[0];out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),d[16:],len(d)-16)==n*56;return out.raw
def matches(hay,needle):
 out=[];p=0
 while True:
  p=hay.find(needle,p)
  if p<0:return out
  if p%56==0:out.append(p//56)
  p+=1
raw=load(r/'raw-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin')
native=load(r/'ops.bin');assert native==final;del native
assert hashlib.sha256((r/'raw-builder.bin').read_bytes()).hexdigest()=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69'
folds={}
for line in(r/'fold-marks.tsv').read_text().splitlines():
 f=line.split('\t');at,ident,before,rev,t=map(int,f[:5])
 if before:folds[ident]=dict(raw_begin=at,reverse=bool(rev),tick=t,acc=list(map(int,f[5].split(','))))
 else:folds[ident]['raw_end']=at
prior=json.loads((r.parent/'precision-repair-20261016/surviving-folds.json').read_text())
prior_by={(x['reverse'],x['tick']):x for x in prior['rows']}
edited=json.loads((r.parent/'prefilter-20261015/a29-edited-folds-v1/original-candidates.json').read_text())
ed_by={x['hint']['tick']:x['mapping']for x in edited['rows']}
marks=[json.loads(x.split('VALUE_TERMINAL ',1)[1])for x in(r/'observer.log').read_text().splitlines()if x.startswith('VALUE_TERMINAL ')]
rows=[]
for mark in marks:
 containing=[x for x in folds.values()if x['raw_begin']<=mark['begin']<mark['end']<=x['raw_end']]
 if len(containing)!=1:continue
 fold=containing[0]
 # The separately generated finite seed calls fold_fwd_v2 before body() has
 # established its payload context. Preserve it as an explicit unbound seed,
 # rather than attributing its sentinel tick to a normal forward body.
 body_context=(fold['reverse'],fold['tick'])==(mark['rev'],mark['tick'])
 assert body_context or mark['tick']==N,(fold,mark)
 row=dict(mark,fold=fold,body_payload_context_bound=body_context)
 row['rev']=fold['reverse'];row['tick']=fold['tick']
 lo,hi=mark['begin'],mark['end'];block=raw[lo*56:hi*56]
 row['old_local_sha256']=hashlib.sha256(block).hexdigest();row['local_matches']=matches(final,block)
 pp=prior_by[(row['rev'],row['tick'])]
 if pp['found']:
  a=pp['final_start'];b=a+pp['ops'];assert raw[fold['raw_begin']*56:fold['raw_end']*56]==final[a*56:b*56]
  row['actual_fold']=[a,b];row['full_fold_byte_identical']=True
 elif not mark['rev']and mark['tick']in ed_by:
  e=ed_by[mark['tick']];a,b=e['start'],e['end_exclusive']
  assert raw[fold['raw_begin']*56:(fold['raw_begin']+16)*56]==final[a*56:(a+16)*56]
  assert raw[(fold['raw_end']-16)*56:fold['raw_end']*56]==final[(b-16)*56:b*56]
  row['actual_fold']=[a,b];row['full_fold_byte_identical']=False
 else:row['actual_fold']=None
 row['local_matches_within_fold']=[p for p in row['local_matches']if row['actual_fold']and row['actual_fold'][0]<=p and p+(hi-lo)<=row['actual_fold'][1]]
 if len(row['local_matches_within_fold'])==1:
  start=row['local_matches_within_fold'][0];row['actual_ccx']=start+mark['ccx']-lo
  o=struct.unpack_from('<7Q',final,row['actual_ccx']*56)
  assert o==(13,mark['ha'],mark['hb'],mark['top'],N,N,N),o
  a,b=row['actual_fold'];used={q for op in struct.iter_unpack('<7Q',final[a*56:b*56])for q in op[1:4]if q!=N}
  row['next_bit_framed_by_entire_actual_old_fold']=mark['next']!=N and mark['next']not in used
  row['old_complete_fold_sha256']=hashlib.sha256(final[a*56:b*56]).hexdigest()
 row['equal_top_two_sign_forms']=mark['sign']==mark['top_sign']and mark['sign_one']==mark['top_sign_one']
 row['sign_extension_source_bound']=mark['hi']>=41 and row['equal_top_two_sign_forms']
 row['a_host_proved_expected']=mark['ha']==mark['acc'][-2]and mark['a']==[mark['acc'][-2],mark['ci']]and not mark['a_one']
 row['c_alias_b']=mark['hb']==mark['ci'];row['logical_c_extra_constant']=row['c_alias_b']and mark['b_one']
 rows.append(row)
print('TERMINAL_INTERFACE',len(rows),collections.Counter((x['rev'],len(x['local_matches_within_fold']),x.get('next_bit_framed_by_entire_actual_old_fold'))for x in rows),flush=True)
queries=sorted({x['actual_ccx']for x in rows if'actual_ccx'in x})
nq=1234;nb=45701;initialq=(ctypes.c_int8*nq)();initialb=(ctypes.c_int8*nb)();abi=set()
for k,a,b,t,bt,bc,rt in struct.iter_unpack('<7Q',final):
 if k==2:
  if t!=N:initialq[t]=-1
  if bt!=N:initialb[bt]=-1;abi.add(bt)
assert abi==set(range(512))
libpath=r.parent/'precision-family-20261016/constant_zero.so';lib=ctypes.CDLL(str(libpath))
lib.constant_zeros.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t),ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p];lib.constant_zeros.restype=ctypes.c_int
qq=(ctypes.c_size_t*len(queries))(*queries);zeros=ctypes.create_string_buffer(len(queries)*nq)
assert lib.constant_zeros(final,len(final)//56,nq,nb,qq,len(queries),zeros,initialq,initialb)==0
zero_at={p:[i for i in range(nq)if zeros.raw[n*nq+i]]for n,p in enumerate(queries)}
state=ClassicalGuards(nb,abi);guards={};queryset=set(queries)
for at,(k,a,b,t,bt,bc,rt)in enumerate(struct.iter_unpack('<7Q',final)):
 if at in queryset:assert bc==N;guards[at]=state.snapshot()
 state.step(k,None if bt==N else bt,None if bc==N else bc,at)
assert not state.stack and state.mr==906156
for x in rows:
 if'actual_ccx'not in x:continue
 at=x['actual_ccx'];x['guard']=guards[at]
 excluded={x[k]for k in['ha','hb','ci','top','next']}|set(x['a'])|set(x['b'])
 x['global_zero_short_donors']=[q for q in zero_at[at]if q not in excluded]
 x['dirty_short_donors']=[q for q in range(nq)if q not in excluded]
 x['complete_source_interface_admitted']=all([x['next_bit_framed_by_entire_actual_old_fold'],x['sign_extension_source_bound'],x['a_host_proved_expected']])
families={}
for name,pred in [('all_forward',lambda x:not x['rev']),('late_forward_source_window56',lambda x:not x['rev']and x['tick']>=100),('all_reverse',lambda x:x['rev']),('late_reverse_source_tick100plus',lambda x:x['rev']and x['tick']>=100)]:
 selected=[x for x in rows if pred(x)];cost=sum((Fraction(x['guard']['upper'])for x in selected if'guard'in x),Fraction())
 families[name]=dict(source_sites=len(selected),local_unique=sum('actual_ccx'in x for x in selected),complete_interface=sum(x.get('complete_source_interface_admitted',False)for x in selected),global_zero_short_donor_sites=sum(bool(x.get('global_zero_short_donors'))for x in selected),
  projected_clean_cost_upper=str(cost),projected_dirty_cost_upper=str(4*cost),
  unresolved_sites=[x['tick']for x in selected if not x.get('complete_source_interface_admitted',False)])
report=dict(status='SOURCE INTERFACE/COST DIAGNOSTIC; NO CANDIDATE/FAMILY FROZEN',rows=rows,families=families,
 guards_tests=tests(),raw_sha256=hashlib.sha256((r/'raw-builder.bin').read_bytes()).hexdigest(),native_sha256=hashlib.sha256((r/'ops.bin').read_bytes()).hexdigest(),native_equals_frozen_final_canonical=True,constant_zero_library_sha256=hashlib.sha256(libpath.read_bytes()).hexdigest(),
 dependency_edited_boundaries_sha256=hashlib.sha256((r.parent/'prefilter-20261015/a29-edited-folds-v1/original-candidates.json').read_bytes()).hexdigest())
(r/'terminal-interfaces.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(families,indent=2))
