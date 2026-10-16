from bisect import bisect_right

def find_matches(op,n,positions,barriers,ccx,span_digest):
 def next_touch(i,wires):
  out=n
  for q in wires:
   p=positions[q];j=bisect_right(p,i)
   if j<len(p):out=min(out,p[j])
  return out
 matches=[];first_two=0
 for i in ccx:
  _,a0,b0,t,_,c,_=op(i)
  if len({a0,b0,t})!=3:continue
  for a,b in [(a0,b0),(b0,a0)]:
   j=next_touch(i,{a,b,t})
   if j==n:continue
   k1,aa,bb,tt,bt,cc,rr=op(j)
   if not(k1==8 and bb==a and tt==b and cc==c):continue
   first_two+=1
   k=next_touch(j,{a,b,t})
   if k==n:continue
   k2,u,v,target,_,guard,_=op(k)
   if not(k2==13 and target==t and guard==c and b in(u,v)):continue
   other=v if u==b else u
   if len({a,b,other,t})!=4:continue
   if next_touch(i,{other})!=k:continue
   end=next_touch(k,{a,b,other,t})
   if end==n:continue
   k3,_,ctrl,target,_,guard,_=op(end)
   if not(k3==8 and ctrl==a and target==b and guard==c):continue
   barrier=bisect_right(barriers,i)
   if barrier<len(barriers)and barriers[barrier]<=end:continue
   indices=[i,j,k,end]
   matches.append({'begin':i,'end_exclusive':end+1,'macro_indices':indices,'a':a,'b':b,'c':other,'t':t,
    'direct_classical_condition':None if c==2**64-1 else c,'contiguous':indices==list(range(i,i+4)),
    'span_sha256':span_digest(i,end+1),'intervening_ops':end+1-i-4})
 return matches,first_two
