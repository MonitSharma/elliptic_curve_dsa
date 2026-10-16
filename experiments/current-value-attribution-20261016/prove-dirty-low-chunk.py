from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent
rows=json.loads((r/'tick131-first-add-ops.json').read_text())['first80'][:31]
assert [x['at']for x in rows]==list(range(4052107,4052138))
ZERO=frozenset();ONE=frozenset([frozenset()])
def var(i):return frozenset([frozenset([i])])
def xor(a,b):return a^b
def mul(a,b):
 out=set()
 for x in a:
  for y in b:
   term=x|y
   if term in out:out.remove(term)
   else:out.add(term)
 return frozenset(out)
def maj(a,b,c):return xor(xor(mul(a,b),mul(a,c)),mul(b,c))
A=[256,257,258,259];B=[764,699,852,853];D=[554,555,556,553]
initial={q:var(i)for i,q in enumerate(A+B+D)}
q=dict(initial);bits={};phase=ZERO;draw=0;mr=[]
for row in rows:
 k,c2,c1,t,bt,bc,reg=row['fields'];g=ONE if bc==2**64-1 else bits[bc]
 if k==8:q[t]=xor(q.get(t,ZERO),mul(g,q[c1]))
 elif k==13:q[t]=xor(q.get(t,ZERO),mul(g,mul(q[c1],q[c2])))
 elif k==9:phase=xor(phase,mul(g,mul(q[c1],q[t])))
 elif k in [11,12]:
  fresh=var(12+draw);draw+=1;phase=xor(phase,mul(g,mul(q[t],fresh)));q[t]=mul(xor(ONE,g),q[t])
  if k==12:bits[bt]=fresh;mr.append((t,fresh))
 else:raise AssertionError(k)
assert draw==6 and len(mr)==3
ci=ZERO;want={};cs=[]
for i in range(4):
 a,b=initial[A[i]],initial[B[i]]
 want[B[i]]=a^b^ci;ci=initial[D[i]]^maj(a,b,ci);cs.append(ci)
for i in range(4):assert q[A[i]]==initial[A[i]] and q[B[i]]==want[B[i]]
assert all(q[d]==ZERO for d in D[:3]) and q[D[3]]==cs[3]
expected_phase=ZERO
for target,m in mr:expected_phase^=mul(m,initial[target])
assert phase==expected_phase and phase!=ZERO
# Exact signed integer effect for a single dirty internal carry, with all
# other scratch bits clean. This is a diagnosis, not an admitted repair.
def ev(poly,v):return sum(all(v>>i&1 for i in mon)for mon in poly)%2
integer=0
for a in range(16):
 for b in range(16):
  for dirty in range(3):
   v=a|(b<<4)|(1<<(8+dirty));got=sum(ev(q[B[i]],v)<<i for i in range(4))+(ev(q[D[3]],v)<<4)
   true_c=((a%(1<<(dirty+1)))+(b%(1<<(dirty+1))))>>(dirty+1)
   assert got==a+b+(1-2*true_c)*(1<<(dirty+1));integer+=1
out=dict(status='PASS: EXACT ACTUAL FIRST4BIT CHUNK DIRTY-ENTRY CHARACTERIZATION',original_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',actual_original_span=[4052107,4052138],actual_op_rows_sha256=hashlib.sha256(json.dumps([x['fields']for x in rows],separators=(',',':')).encode()).hexdigest(),
 universal_quantum_entry_variables=12,universal_physical_MR_variables=6,uncapped_canonical_square_free_ANF=True,
 input_q=A+B+D,sum='sum[i] = a[i] XOR b[i] XOR c[i], c[0]=0; c[i+1]=dirty[i] XOR MAJ(a[i],b[i],c[i])',
 source='all four original bits restored',scratch='three internal dirty carries reset to0; output dirty carry equals olddirty XOR actual carry',
 exact_phase='incoming_phase XOR HMR0*dirty0 XOR HMR1*dirty1 XOR HMR2*dirty2; all three extra R draws remain consumed',
 arbitrary_external_snapshot_guard='if0, identity; if1, displayed exact contract; MR consumed either way',
 ordinary_clean_arithmetic_and_phase_recovered_iff='all four scratch entry bits0 (the normal sufficient clean-adder premise)',
 false_clean_phase_negative_control_detected=phase!=ZERO,single_dirty_carry_integer_cases=integer,
 no_repair=True,no_discard_or_classicalization_justified=True)
(r/'dirty-low-chunk-proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
