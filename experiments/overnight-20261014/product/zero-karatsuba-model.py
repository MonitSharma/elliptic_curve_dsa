"""Independent unsigned integer model; does not model dirty-wire phase/loan effects."""
from functools import cache
p=2**256-2**32-977;f=2**32+977
def model(topmask=False,tail=None):
 @cache
 def node(m,flat=False):
  lo=m//2;hi=m-lo
  def child(n,threshold,child_flat):
   return node(n,child_flat) if not flat and n>=threshold else 2**(2*n)-2
  a=child(lo,64,False);b=child(hi,64,True);t=child(hi+1,65,False)
  width=2*(hi+1)
  cross=(t-a-(b^2))%(2**width)
  used=cross
  if topmask:
   used &= (1<<(width-(2 if lo<hi else 1)))-1
  initial=a+(b<<(2*lo))
  if tail is None:return (initial+(used<<lo))%(2**(2*m))
  acc_width=min(2*m-lo,width+tail)
  low=initial&((1<<lo)-1);acc=initial>>lo
  acc_low=(acc+used)%(1<<acc_width)
  return low+(acc_low<<lo)+((acc>>acc_width)<<(lo+acc_width))
 a=node(128);b=node(128);c=node(129)
 actual=(a*(1-2**128)+b*(f-2**128)+c*2**128)%p
 return dict(a=a,b=b,c=c,square=actual)
@cache
def formal(m,flat=False):
 lo=m//2;hi=m-lo
 def child(n,threshold,child_flat):return formal(n,child_flat) if not flat and n>=threshold else -2
 a=child(lo,64,False);b=child(hi,64,True);t=child(hi+1,65,False)
 return a+(t-a-b+2)*2**lo+b*2**(2*lo)
offset=(formal(128)*(1-2**128)+formal(128)*(f-2**128)+formal(129)*2**128)%p
observed=int('ffc00001000003d400000b73fffff86100000b7600000b6bffffe54c000e9c14',16)
observed_base=int('fff00002c2a00b770b800b77ffc007a40ba00b71869ffc2adcbfe54c000e9c14',16)
for mask in [False,True]:
 for tail in [None,18]:
  result=model(mask,tail);delta=(result['square']-offset)%p
  print('topmask',mask,'tail',tail,{k:hex(v) for k,v in result.items()},'delta',hex(delta),'matches_full',delta==observed,'matches_baseline',delta==observed_base)
print('formal_offset',hex(offset))
assert (model(True,18)['square']-offset)%p==observed_base
remaining=(observed-(model(True,None)['square']-offset))%p
assert remaining==(-(1<<246))%p
print('DIAGNOSTIC_IDENTITY_CHECK baseline_delta_exact=True full_residual=-2^246_mod_p phase_or_loan_proof=False')
