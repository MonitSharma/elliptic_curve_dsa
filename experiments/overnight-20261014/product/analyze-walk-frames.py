"""Independent unbounded-integer/mod-p model of exact observed tick frames."""
from pathlib import Path
import collections,json,re,sys
p=2**256-2**32-977
inv2=pow(2,-1,p)
path=Path(sys.argv[1]);rows=[]
for line in path.read_text().splitlines():
 if line.startswith('PRODUCT_WALK_FRAME '):rows.append(dict(re.findall(r'(\w+)=(\S+)',line)))
assert rows
def word(r,i):
 if r['r'+str(i)]=='-':return None
 n=int(r['r'+str(i)],16);w=int(r['r'+str(i)+'_width']);assert 0<=n<2**w
 return n-2**w if n>>(w-1)else n
def payload(r):return None if r['p0']=='-'else [int(r['p'+str(i)],16)%p for i in range(2)]
def tick_transform(target,source,letter,reverse=False,skip=False,mod=None):
 assert len(letter)in[3,5]
 signs=[1 if s=='0'else -1 for s in letter[:-2]];e=int(letter[-2])+2*int(letter[-1]);remainders=[]
 if reverse:
  target*=2**e
  for sign in signs[::-1]:target=2*target-sign*source
 else:
  for sign in signs:
   target+=sign*source
   if mod is None:remainders.append(target%2);target//=2
   else:target=target*inv2%mod
  if not skip:
   if mod is None:remainders.append(target%(2**e));target//=2**e
   else:target=target*pow(2**e,-1,mod)%mod
 return (target%mod if mod else target),remainders
# Meaningful independent algebraic inverse checks, including negative rails and noncanonical payload representatives.
for t,b in [(135,-17),(-101,21),(0,p),(p,p-1)]:
 for letter in ['00000','01011','11110','011']:
  f,_=tick_transform(t,b,letter,mod=p);r,_=tick_transform(f,b,letter,reverse=True,mod=p);assert r==t%p
faults=[];parks=[];pairs=0
groups=collections.defaultdict(list)
for r in rows:groups[(r['source'],r['mode'],r['index'])].append(r)
for key,rs in groups.items():
 assert all(int(a['seq'])<int(b['seq'])for a,b in zip(rs,rs[1:]))
 for n,a in enumerate(rs):
  if a['label']in['div_before_endpoint','mul_before_endpoint']:
   rr=[word(a,i)for i in range(2)];parks.append(dict(source=key[0],mode=key[1],index=int(key[2]),scope=a['scope'],seq=int(a['seq']),rails=rr,parked=all(abs(r)==1 for r in rr)))
  if not a['label'].endswith('_before'):continue
  b=rs[n+1];assert b['label']==a['label'].replace('_before','_after')and(a['scope'],a['t'])==(b['scope'],b['t'])
  reverse='rev'in a['label'];letter=a['letter']if reverse else b['letter'];t=int(a['t']);ti=t%2;si=1-ti
  if letter=='-':continue
  assert len(letter)in[3,5],(a,letter)
  bad={};pa,pb=payload(a),payload(b)
  if pa is not None:
   expected,_=tick_transform(pa[ti],pa[si],letter,reverse=reverse,skip=a['skip']=='true',mod=p)
   if expected!=pb[ti]or pa[si]!=pb[si]:bad['payload']=dict(expected_target=hex(expected),actual_target=hex(pb[ti]),delta=hex((pb[ti]-expected)%p),source_preserved=pa[si]==pb[si])
  ra,rb=[word(a,i)for i in range(2)],[word(b,i)for i in range(2)]
  if ra[0]is not None:
   expected,rems=tick_transform(ra[ti],ra[si],letter,reverse=reverse)
   if expected!=rb[ti]or ra[si]!=rb[si]or any(rems):bad['rails']=dict(expected_target=expected,actual_target=rb[ti],source_preserved=ra[si]==rb[si],nonexact_divisions=any(rems),output_width=int(b['r'+str(ti)+'_width']),expected_fits_output=-(2**(int(b['r'+str(ti)+'_width'])-1))<=expected<2**(int(b['r'+str(ti)+'_width'])-1))
  pairs+=1
  if bad:faults.append(dict(source=key[0],mode=key[1],index=int(key[2]),scope=a['scope'],family=a['label'].removesuffix('_before'),t=t,seq=int(a['seq']),old_start=int(a['old_end']),old_end=int(b['old_end']),letter=letter,bad=bad))
first={}
for f in faults:
 key=f"{f['source']}:{f['mode']}:{f['index']}:{f['scope']}"
 first.setdefault(key,f)
out=dict(status='FINITE_SOURCE_BOUND_DIAGNOSTIC',qualified_score=None,frames=len(rows),points=len(groups),modeled_tick_pairs=pairs,source_rule='cells::add_halve T=(T+(-1)^s B)/2 modp; reverse with X(s) gives T=2T-(-1)^s B; barrel exponents k1+2k2; rails same integer transformations with exact division and observed signed widths.',limitations='Current pass checks entire source ticks against actual incoming state, not every internal cell. Does not prove tape sign/choice intended or global convergence. Endpoint rails checked separately. Cross-source MR unaligned.',first_tick_failure=first,endpoint_parks=parks,fault_count=len(faults),faults=faults)
dest=Path(sys.argv[2]);dest.write_text(json.dumps(out,indent=2)+'\n',newline='\n')
print(json.dumps(dict(frames=len(rows),tick_pairs=pairs,first_faults=first,nonparked=[r for r in parks if not r['parked']]),indent=2))
