"""Reconstruct the actual core and check every native truth-table bit first."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;native=r.parent/'breakthrough-core-rank-20261020/CORE-TRUTH.json';data=json.loads(native.read_bytes());mask=(1<<256)-1
truth=[sum(v<<(64*j)for j,v in enumerate(words))for words in data['qubit_truth_words']];wires=truth[:8].copy();gates=[]
def aand(a,b):
 v=a&b;gates.append({'a':a,'b':b,'xor':0});wires.append(v);return v
def maj(x,y,c):
 a=x^c;b=y^c;v=(a&b)^c;gates.append({'a':a,'b':b,'xor':c});wires.append(v);return v
n=wires[:8];s=n[7];q=[n[0],n[1],n[2]^n[0]];d=aand(n[2]^mask,n[0])
for i in range(3,9):
 ni=n[i]if i<8 else n[7];q.append(ni^n[i-2]^d);d=maj(ni^mask,n[i-2],d)
q.append(d);j=q[6:10];u=[n[0]^j[0]];e=aand(n[0],j[0])
for i in range(1,7):
 ji=j[i]if i<4 else j[3];u.append(n[i]^ji^e)
 if i<6:e=maj(n[i],ji,e)
h=[n[0]^s];z=aand(n[0]^mask,s)
for i in range(1,7):
 h.append(n[i]^z)
 if i<6:z=aand(n[i]^mask,z)
outputs=[]
for b in range(len(data['output_forms'])):outputs.append(0 if b<4 else q[b-4]if b<10 else u[b-10]if b<17 else s if b<32 else h[b-32]if b<39 else s)
assert len(gates)==19 and wires==truth
for value,form in zip(outputs,data['output_forms']):
 expected=mask if form['one']else 0
 for index in form['wires']:expected^=truth[index]
 assert value==expected
def words(v):return[(v>>(64*j))&((1<<64)-1)for j in range(4)]
rows=[f'8 {len(outputs)} {len(gates)} 3']
for v in n+outputs+[v for g in gates for v in[g['a'],g['b']]]+[wires[i]for i in[12,13,14]]:rows.append(' '.join(map(str,words(v))))
(r/'instance.dat').write_text('\n'.join(rows)+'\n')
serial={'inputs':[hex(v)for v in n],'outputs':[hex(v)for v in outputs],'gates':[{k:hex(v)for k,v in g.items()}for g in gates],'lift_functions':{str(i):hex(wires[i])for i in[12,13,14]},'native_truth_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'instance_sha256':hashlib.sha256((r/'instance.dat').read_bytes()).hexdigest(),'scope':'All19 native held functions and every output form match on all256 values. Actual n=-128 behavior preserved. No circuit edit or scored result.'}
(r/'INSTANCE-VERIFICATION.json').write_text(json.dumps(serial,indent=2)+'\n');print('All native functions and outputs match; exact instance frozen.')
