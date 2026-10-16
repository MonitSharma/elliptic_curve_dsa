from collections import defaultdict
from pathlib import Path
import json
from patterns import find_matches
N=2**64-1
def gate(k,a=N,b=N,t=N,c=N):return(k,a,b,t,N,c,N)
base=[gate(13,0,1,3),gate(8,b=0,t=1),gate(13,1,2,3),gate(8,b=0,t=1)]
def scan(ops):
 pos=defaultdict(list);barriers=[];ccx=[]
 for i,o in enumerate(ops):
  for q in set(o[1:4])-{N}:pos[q].append(i)
  if o[0]not in{0,6,7,8,9,10,13,14}:barriers.append(i)
  if o[0]==13:ccx.append(i)
 return find_matches(ops.__getitem__,len(ops),pos,barriers,ccx,lambda a,b:'synthetic')[0]
checks=[]
def test(name,ops,expected):
 found=scan(ops);assert bool(found)==expected,name
 checks.append({'name':name,'expected_match':expected,'matches':len(found)})
test('exact contiguous',base,True)
test('controls reversed',[gate(13,1,0,3),base[1],gate(13,2,1,3),base[3]],True)
test('independent pure gates',[base[0],gate(6,t=8),gate(9,b=8,t=9,c=1),base[1],base[2],gate(0,c=2),base[3]],True)
test('fourth wire earlier observation',[base[0],gate(7,t=2),*base[1:]],False)
test('changed control observed',[base[0],base[1],gate(7,t=1),*base[2:]],False)
for kind in [1,2,3,4,5,11,12,15,16,17]:
 test('barrier '+str(kind),[base[0],gate(kind,t=8,c=5),*base[1:]],False)
for i in range(1,4):
 changed=list(base);changed[i]=(*changed[i][:5],7,N);test('different guard '+str(i),changed,False)
bad=list(base);bad[2]=gate(13,1,0,3);test('fourth wire alias',bad,False)
test('unfinished',[*base[:3]],False)
test('two copies',[*base,*base],True)
assert len(scan([*base,*base]))==2
report={'status':'SHARED_ACTUAL_SCANNER_POSITIVE_AND_ADVERSARIAL_PATTERN_TESTS_PASS','checks':checks}
Path(__file__).with_name('PATTERN-TESTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks)}))
