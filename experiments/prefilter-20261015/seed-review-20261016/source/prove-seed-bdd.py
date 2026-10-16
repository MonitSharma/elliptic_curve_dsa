from pathlib import Path
import json,struct,ctypes,ctypes.util,hashlib,collections
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');N=2**64-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
class BDD:
 def __init__(self):self.nodes=[(10**9,0,0),(10**9,1,1)];self.unique={};self.memo={}
 def node(self,v,l,h):
  if l==h:return l
  key=(v,l,h)
  if key not in self.unique:
   assert len(self.nodes)<1000000,'RESOURCE UNKNOWN';self.unique[key]=len(self.nodes);self.nodes.append(key)
  return self.unique[key]
 def op(self,and_,x,y):
  x,y=sorted([x,y])
  if and_:
   if x==0:return 0
   if x==1 or x==y:return y
  else:
   if x==0:return y
   if x==y:return 0
  key=(and_,x,y)
  if key in self.memo:return self.memo[key]
  v=min(self.nodes[x][0],self.nodes[y][0]);xl,xh=self.nodes[x][1:]if self.nodes[x][0]==v else(x,x);yl,yh=self.nodes[y][1:]if self.nodes[y][0]==v else(y,y)
  out=self.node(v,self.op(and_,xl,yl),self.op(and_,xh,yh));self.memo[key]=out;return out
 def xor(self,x,y):return self.op(False,x,y)
 def mul(self,x,y):return self.op(True,x,y)
 def neg(self,x):return self.xor(x,1)
def prove(ops,target,dirty=False):
 b=BDD();used={v for o in ops for v in o[1:4]if v!=N};scratch=sorted(used-set(target));q={i:0 for i in used};initial=[]
 for i,qid in enumerate(target):q[qid]=b.node(i*2,0,1);initial.append(q[qid])
 if dirty:
  for i,qid in enumerate(scratch):q[qid]=b.node(i*2+1,0,1)
 entry=q.copy();cb={};phase={};mr=0;stack=[];base=1
 def ph(m,c):
  phase[m]=b.xor(phase.get(m,0),c)
 for at,o in enumerate(ops):
  k,c2,c1,t,bt,cond,rt=o
  # This helper has no quantum/classical mixing beyond MR-controlled phase.
  if cond!=N:assert k in [7,9,14]and cond in cb;guard=cb[cond]
  else:guard=None
  if k in [6,8,13]:
   assert guard is None and not stack
   x=1 if k==6 else q[c1]
   if k==13:x=b.mul(x,q[c2])
   q[t]=b.xor(q[t],x)
  elif k==10:assert guard is None;q[t],q[c1]=q[c1],q[t]
  elif k in [11,12]:
   assert guard is None and not stack;ph(mr,q[t]);q[t]=0
   if k==12:cb[bt]=mr
   mr+=1
  elif k in [7,9,14]:
   assert guard is not None
   c=q[t]
   if k in [9,14]:c=b.mul(c,q[c1])
   if k==14:c=b.mul(c,q[c2])
   ph(guard,c)
  else:raise AssertionError(('unsupported',at,o))
 # Independent binary-borrow reference for exact finite low53 subtraction.
 borrow=0;adjusted=[];f=0x1000003d1
 for i in range(53):
  a=initial[i];k=initial[0]if f>>i&1 else 0
  adjusted.append(b.xor(b.xor(a,k),borrow));na=b.neg(a)
  borrow=b.xor(b.xor(b.mul(na,k),b.mul(na,borrow)),b.mul(k,borrow))
 assert adjusted[0]==0
 want=adjusted[1:]+initial[53:]+[initial[0]]
 bad=[i for i,w in enumerate(target)if q[w]!=want[i]];dirty_out=[w for w in scratch if q[w]!=0];phase_nonzero=[m for m,c in phase.items()if c!=0]
 return dict(all256_target_bits_match_finite53_formula=not bad,target_unresolved_bits=bad,scratch_preconditions_zero=scratch if not dirty else[],all_scratch_restored_zero=not dirty_out,nonzero_scratch=dirty_out,phase_exact_zero=not phase_nonzero,nonzero_MR_phase_coefficients=phase_nonzero,MR_draws=mr,BDD_nodes=len(b.nodes),all256_target_entry_bits_arbitrary=True,all_internal_MR_arbitrary=True,dirty_entry_test=dirty)
m=json.loads((r/'actual-seed-markers.json').read_text());a,e=m['markers'];raw=load(r/'raw-seed-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin');decode=lambda d,x,y:[struct.unpack_from('<7Q',d,i*56)for i in range(x,y)]
original=decode(raw,a['raw_at'],e['raw_at']);current=decode(final,a['at'],e['at']);good=prove(original,a['target']);bad=prove(current,a['target']);assert good['all256_target_bits_match_finite53_formula']and good['all_scratch_restored_zero']and good['phase_exact_zero'];assert not bad['all256_target_bits_match_finite53_formula']
out=dict(status='EXACT BDD CLEAN-SCRATCH SEED CONTRACT PASS; inherited helper negative preserved',original_source=good,current_inherited_negative=bad,source_raw_region_sha256=hashlib.sha256(raw[a['raw_at']*56:e['raw_at']*56]).hexdigest(),actual_region_sha256=hashlib.sha256(final[a['at']*56:e['at']*56]).hexdigest(),note='Prefix zero proof required before applying clean-scratch theorem; no arbitrary-dirty correctness promise')
(r/'seed-bdd-contract.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
