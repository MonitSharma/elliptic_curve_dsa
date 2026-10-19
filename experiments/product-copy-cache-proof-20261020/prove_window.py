"""Independent one-shot symbolic semantics, including phase and physical draws."""
import gzip,hashlib,json,time,unittest
from collections import Counter
from pathlib import Path
import z3
NO=2**64-1;r=Path(__file__).resolve().parent
def cache_rows(ops,first,last,storage):
    out=[]
    for i,row in enumerate(ops):
        k,b,a,t,ct,cc,reg=row
        if i==first:out.extend([[13,b,a,storage,ct,cc,reg],[8,NO,storage,t,NO,NO,NO]])
        elif i==last:out.extend([[8,NO,storage,t,NO,NO,NO],[8,NO,t,storage,NO,NO,NO]])
        else:out.append(row)
    return out
def symbolic_equivalence(old,new,timeout=60000,save=None):
    ctx=z3.Context(proof=True);variables={}
    def bit(kind,index):return variables.setdefault((kind,index),z3.Bool(kind+str(index),ctx=ctx))
    false=z3.BoolVal(False,ctx=ctx);true=z3.BoolVal(True,ctx=ctx)
    def run(ops):
        q={};c={};base=true;stack=[];phase=[];draws=0
        def qb(w):assert w!=NO;return q.setdefault(w,bit('q',w))
        def cb(w):assert w!=NO;return c.setdefault(w,bit('c',w))
        def put(table,w,value):table[w]=z3.simplify(value)
        def flip(value):
            value=z3.simplify(value)
            if not z3.is_false(value):phase.append(value)
        for k,b,a,t,ct,cc,reg in ops:
            if k==15:stack.append(base);base=z3.simplify(z3.And(base,cb(cc)));continue
            if k==16:base=stack.pop();continue
            cond=base if cc==NO else z3.simplify(z3.And(base,cb(cc)))
            if k==13:put(q,t,z3.Xor(qb(t),z3.And(cond,qb(a),qb(b))))
            elif k==8:put(q,t,z3.Xor(qb(t),z3.And(cond,qb(a))))
            elif k==6:put(q,t,z3.Xor(qb(t),cond))
            elif k==10:
                qa,qt=qb(a),qb(t);put(q,a,z3.If(cond,qt,qa));put(q,t,z3.If(cond,qa,qt))
            elif k in [11,12]:
                m=bit('rng',draws);draws+=1;flip(z3.And(cond,qb(t),m));put(q,t,z3.And(qb(t),z3.Not(cond)))
                if k==12:put(c,ct,z3.If(cond,m,cb(ct)))
            elif k==3:put(c,ct,z3.Xor(cb(ct),cond))
            elif k==4:put(c,ct,z3.And(cb(ct),z3.Not(cond)))
            elif k==5:put(c,ct,z3.Or(cb(ct),cond))
            elif k==0:flip(cond)
            elif k==7:flip(z3.And(cond,qb(t)))
            elif k==9:flip(z3.And(cond,qb(a),qb(t)))
            elif k==14:flip(z3.And(cond,qb(a),qb(b),qb(t)))
            elif k in [1,2,17]:pass
            else:raise ValueError(k)
        assert not stack
        return q,c,phase,draws
    a=run(old);b=run(new);assert a[3]==b[3]
    differences=[]
    for field,prefix in [(0,'q'),(1,'c')]:
        for index in sorted(a[field].keys()|b[field].keys()):differences.append(z3.Xor(a[field].get(index,bit(prefix,index)),b[field].get(index,bit(prefix,index))))
    # Cancel identical phase terms first; retain every unmatched term exactly.
    terms={};counts=Counter()
    for term in a[2]+b[2]:key=term.get_id();terms[key]=term;counts[key]+=1
    phase=false
    for key,count in counts.items():
        if count%2:phase=z3.Xor(phase,terms[key])
    differences.append(phase);solver=z3.Solver(ctx=ctx);solver.set(timeout=timeout,threads=1);solver.add(z3.Or(*differences));start=time.monotonic();verdict=solver.check()
    result={'verdict':str(verdict),'seconds':time.monotonic()-start,'quantum_wires_compared':len(a[0].keys()|b[0].keys()),'classical_bits_compared':len(a[1].keys()|b[1].keys()),'phase_compared':True,'physical_draw_count_each':a[3],'arbitrary_boundary_and_rng_variables':len(variables),'solver_version':z3.get_version_string(),'scope':'All boundary basis values and every physical RNG assignment, including global phase. SAT at an unseeded window may be an unreachable boundary; it is not a failed circuit gate.'}
    if save:
        with gzip.open(str(save)+'.smt2.gz','wt') as f:f.write(solver.to_smt2())
        if verdict==z3.unsat:
            with gzip.open(str(save)+'.proof.gz','wt') as f:f.write(str(solver.proof()))
            replay=z3.Solver(ctx=ctx);replay.from_string(gzip.open(str(save)+'.smt2.gz','rt').read());replay.set(timeout=timeout,threads=1);assert replay.check()==z3.unsat;result['saved_smt2_replayed']=True
        elif verdict==z3.sat:
            with gzip.open(str(save)+'.model.gz','wt') as f:f.write(str(solver.model()))
        Path(str(save)+'.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
def row(k,t,a=NO,b=NO,ct=NO,cc=NO):return [k,b,a,t,ct,cc,NO]
class Tests(unittest.TestCase):
    def base(self):return [row(11,4),row(13,2,0,1),row(12,3,ct=0),row(13,3,0,1)]
    def test_good_all_state_phase_rng(self):
        v=self.base();self.assertEqual(symbolic_equivalence(v,cache_rows(v,1,3,4))['verdict'],'unsat')
    def test_changed_product_is_detected(self):
        v=self.base();v.insert(2,row(6,0));self.assertEqual(symbolic_equivalence(v,cache_rows(v,1,4,4))['verdict'],'sat')
    def test_dirty_consumer_is_detected(self):
        v=self.base();v.pop(2);self.assertEqual(symbolic_equivalence(v,cache_rows(v,1,2,4))['verdict'],'sat')
    def test_dirty_storage_is_detected(self):
        v=self.base()[1:];self.assertEqual(symbolic_equivalence(v,cache_rows(v,0,2,4))['verdict'],'sat')
    def test_phase_only_storage_touch_is_detected(self):
        v=self.base();v.insert(2,row(7,4));self.assertEqual(symbolic_equivalence(v,cache_rows(v,1,4,4))['verdict'],'sat')
    def test_missing_cache_cleanup_is_detected(self):
        v=self.base();w=cache_rows(v,1,3,4);w.pop();self.assertEqual(symbolic_equivalence(v,w)['verdict'],'sat')
if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);assert unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    data=json.loads((r/'WINDOW.json').read_text());audit=json.loads((r/'EDIT-AUDIT.json').read_text());assert hashlib.sha256((r/'WINDOW.json').read_bytes()).hexdigest()==audit['window_sha256']
    result=symbolic_equivalence(data['ops'],cache_rows(data['ops'],data['first_offset'],data['last_offset'],data['storage']),save=r/'local-window')
    print(json.dumps(result,indent=2));(r/'LOCAL-WINDOW-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
