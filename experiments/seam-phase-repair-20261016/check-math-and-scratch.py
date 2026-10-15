from pathlib import Path
import struct,json,hashlib
r=Path(__file__).parent;data=(r/'front_seam.bin').read_bytes();n,m=struct.unpack_from('<2I',data,8);rows=list(struct.iter_unpack('<7Q',data[16:16+n*56]));meta=json.loads((r/'region.json').read_text());none=2**64-1
q=[0]*1234;b=[0]*45701
for i in range(512):q[i]=-1;b[i]=-1
def land(x,y):return 0 if x==0 or y==0 else 1 if x==y==1 else -1
def xor(x,y):return -1 if x<0 or y<0 else x^y
def store(old,c,new):return old if c==0 else new if c==1 or old==new else -1
base=1;stack=[]
for i,(k,z,a,t,bt,bc,reg)in enumerate(rows[:meta['component_offset']]):
 c=base if bc==none else land(base,b[bc])
 if k==6:q[t]=xor(q[t],c)
 elif k==8:q[t]=xor(q[t],land(c,q[a]))
 elif k==13:q[t]=xor(q[t],land(c,land(q[a],q[z])))
 elif k==10:
  x,y=q[t],q[a];q[t]=store(x,c,y);q[a]=store(y,c,x)
 elif k in[11,12]:
  q[t]=store(q[t],c,0)
  if k==12:b[bt]=store(b[bt],c,-1)
 elif k==3:b[bt]=xor(b[bt],c)
 elif k==4:b[bt]=store(b[bt],c,0)
 elif k==5:b[bt]=store(b[bt],c,1)
 elif k==15:stack.append(base);base=c
 elif k==16:base=stack.pop()
assert not stack and base==1
scratch=json.loads((r/'new-phase-contract.json').read_text())['clean_scratch_preconditions'];assert all(q[w]==0 for w in scratch)
cases=0;repairs=0
for x in range(256):
 for o in range(256):
  d=(x-o)%256;ov=int(x<o)
  for k in range(2,8):
   old=int((d>>(8-k))+(o>>(8-k))>=1<<k)
   low=8-k-1;seed=((d>>low)&1)&((o>>low)&1)
   new=int((d>>(8-k))+(o>>(8-k))+seed>=1<<k)
   expanded=int((d>>low)+(o>>low)>=1<<(k+1))
   assert new==expanded and old<=new<=ov
   assert (ov^new)<=(ov^old)
   repairs+=old!=new;cases+=1
out=dict(component_clean_scratch_proved_for_all_declared_input_MR=scratch,proof_initial_state='all input q/b arbitrary; all auxiliary q/b zero at source seam entry, independently proved by whole-stream prefix propagation',source_data_sha256=hashlib.sha256(data).hexdigest(),all_8bit_subtractions_all_prefix_widths_checked=cases,strict_precision_improvements=repairs,identity='P_k <= P_(k+1) <= [x<ox]',finite_lowfold_and_inherited_cuts='arbitrary low-bit changes permitted; relevant high bits and ov preserved by separately checked actual-middle interface')
(r/'math-and-scratch-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
