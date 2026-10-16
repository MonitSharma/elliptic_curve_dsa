def rank(rows):
 pivots={}
 for row in rows:
  while row:
   p=row.bit_length()-1
   if p in pivots:row^=pivots[p]
   else:pivots[p]=row;break
 return len(pivots)

def product(u,uc,v,vc,n):
 linear=(u if vc else 0)^(v if uc else 0)^(u&v)
 rows=[0]*n
 for i in range(n):
  for j in range(i+1,n):
   if ((u>>i&1)&(v>>j&1))^((u>>j&1)&(v>>i&1)):
    rows[i]^=1<<j;rows[j]^=1<<i
 return uc&vc,linear,rows

def frame_for(u,v,n):
 assert rank([u,v])==2
 matrix=[u,v]
 for i in range(n):
  if rank(matrix+[1<<i])>len(matrix):matrix.append(1<<i)
 assert len(matrix)==n
 reduced=matrix.copy();operations=[]
 for col in range(n):
  pivot=next(i for i in range(col,n)if reduced[i]>>col&1)
  if pivot!=col:reduced[pivot],reduced[col]=reduced[col],reduced[pivot];operations.append(('swap',pivot,col))
  for i in range(n):
   if i!=col and reduced[i]>>col&1:reduced[i]^=reduced[col];operations.append(('cx',col,i))
 assert reduced==[1<<i for i in range(n)]
 # Symbolically reconstruct the exact physical frame, including every
 # passenger control wire, rather than assuming rank implies availability.
 check=[1<<i for i in range(n)]
 for kind,a,b in reversed(operations):
  if kind=='swap':check[a],check[b]=check[b],check[a]
  else:check[b]^=check[a]
 assert check==matrix
 return matrix,list(reversed(operations))

def factor(constant,linear,rows):
 n=len(rows);r=rank(rows);assert r in(0,2,4)
 if r==0:return dict(rank=0,constant=constant,linear=linear,frame=[],inverse_frame=[],T=0)
 if r==4:return dict(rank=4,T=2)
 i=next(i for i,row in enumerate(rows)if row);j=(rows[i]&-rows[i]).bit_length()-1
 u,v=rows[j],rows[i]
 fc,fl,fq=product(u,0,v,0,n)
 assert fq==rows and fc==0 and rank([u,v])==2
 matrix,frame=frame_for(u,v,n)
 correction=linear^fl
 # This is an exact coefficient identity over the Boolean ring; all input
 # assignments satisfy it, independent of finite validation fixtures.
 assert product(u,0,v,0,n)[1]^correction==linear
 return dict(rank=2,constant=constant,linear=correction,u=u,v=v,
             frame_matrix=matrix,frame=frame,inverse_frame=list(reversed(frame)),T=1)

def evaluate(constant,linear,rows,x):
 value=constant^((linear&x).bit_count()&1)
 for i,row in enumerate(rows):
  if x>>i&1:value^=((row&x&~((1<<(i+1))-1)).bit_count()&1)
 return value

def execute(f,x,n,target,guard):
 q=[x>>i&1 for i in range(n)];t=target
 if not guard:return x,t
 for kind,a,b in f['frame']:
  if kind=='swap':q[a],q[b]=q[b],q[a]
  else:q[b]^=q[a]
 if f['rank']==2:t^=q[0]&q[1]
 for kind,a,b in f['inverse_frame']:
  if kind=='swap':q[a],q[b]=q[b],q[a]
  else:q[b]^=q[a]
 assert q==[x>>i&1 for i in range(n)]
 t^=f['constant']^((f['linear']&x).bit_count()&1)
 return sum(v<<i for i,v in enumerate(q)),t
