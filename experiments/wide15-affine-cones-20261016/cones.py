from algebra import product,factor
N=2**64-1

def analyze(op,i,n,counts):
 kind,a,b,t,bt,guard,rt=op(i)
 assert kind==13
 forms={};wires={a,b};middle=[]
 def affine(q):return forms.get(q,1<<(q+1))
 for j in range(i+1,min(i+34,n)):
  k,u,v,w,_,g,_=op(j)
  if g!=guard:counts['guard_barrier']+=1;break
  if k==13:
   if w!=t:counts['other_CCX_target_barrier']+=1;break
   if t in(u,v):counts['target_control_barrier']+=1;break
   wires.update((u,v))
   if len(wires)>16:counts['support_cap']+=1;break
   ordered=sorted(wires);where={q:idx for idx,q in enumerate(ordered)};nv=len(ordered)
   def local(q):
    value=affine(q);mask=0
    for wire,idx in where.items():mask|=((value>>(wire+1))&1)<<idx
    assert value>>1==sum(1<<wire for wire in ordered if value>>(wire+1)&1)
    return mask,value&1
   x,xc=local(u);y,yc=local(v)
   c,l,matrix=product(1<<where[a],0,1<<where[b],0,nv)
   c2,l2,q2=product(x,xc,y,yc,nv)
   c^=c2;l^=l2;matrix=[left^right for left,right in zip(matrix,q2)]
   f=factor(c,l,matrix);counts['rank'+str(f['rank'])]+=1
   return {'begin':i,'end_exclusive':j+1,'middle_ops':len(middle),'target':t,'entry_control_wires':ordered,
    'direct_condition':None if guard==N else guard,'rank':f['rank'],'old_T':2,'new_T':f['T'],
    'syntactic_T_saving':2-f['T'],'polynomial':{'constant':c,'linear':l,'polar_rows':matrix},
    'factorization_and_exact_frame':f}
  if k not in(6,8,10):counts['non_X_CX_SWAP_barrier']+=1;break
  if len(middle)==32:counts['separator_cap']+=1;break
  if(k==8 and v==t)or(k==10 and t in(v,w)):counts['target_read_barrier']+=1;break
  wires.update(q for q in(u,v,w)if q not in(N,t))
  if len(wires)>16:counts['support_cap']+=1;break
  if k==6 and w!=t:forms[w]=affine(w)^1
  elif k==8 and w!=t:forms[w]=affine(w)^affine(v)
  elif k==10:forms[v],forms[w]=affine(w),affine(v)
  middle.append(j)
 return None
