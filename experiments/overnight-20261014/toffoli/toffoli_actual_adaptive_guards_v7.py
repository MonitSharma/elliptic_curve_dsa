"""Exact adaptive C3/C4 carrier and lazyTT source-order/guard proof."""
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from toffoli_guided_joint import combination
from toffoli_quadratic_closure import load

here=Path(__file__).parent
netpath=here/'constructor-netlist.json';net=json.loads(netpath.read_bytes());raw,targets,values=load(net)
proof=json.loads((here/'actual-lean-direct-v3.json').read_bytes());m=proof['core_original_masks']
V=lambda name:combination(m[name],values)
assert V('t3') == (V('r3') ^ V('c3')) & V('y3loan')
assert V('c3') == ((V('acc2') if 'acc2' in m else raw[3]) ^ V('c2')) & ((V('E2') if 'E2' in m else raw[9]) ^ V('c2')) ^ V('c2')
assert V('c4') == (~V('final3')) & V('y3loan')
rows=[]
for m6,m3,m5,my in itertools.product(range(2),repeat=4):
    c4=m6;c3=(1^m6)*m3;assert not(c4 and c3)
    tt_first=m6*m3;need=0;builds=[]
    for trigger in [tt_first,m5,my]:
        builds.append(trigger*(1^need));need|=trigger
    assert sum(builds)==((m6*m3)|m5|my)
    old=4+2*m6;new=2+c4+c3+m6+sum(builds)
    rows.append(dict(m6=m6,m3=m3,m5=m5,my=my,C4_guard=c4,C3_guard=c3,TT_builds=builds,old_ANDs=old,new_ANDs=new))
delta=Fraction(sum(row['new_ANDs']-row['old_ANDs'] for row in rows),16);assert delta==Fraction(-15,16)
record={'status':'adaptive_C3_C4_exact16384_identity_and16guardpatterns_verified_native_pending',
        'netlist_sha256':hashlib.sha256(netpath.read_bytes()).hexdigest(),'source_lf_sha256':net['source_lf_sha256'],
        'direct_proof_sha256':hashlib.sha256((here/'actual-lean-direct-v3.json').read_bytes()).hexdigest(),
        'phase_domain_rows':16384,'new_quantum_identity':'T3=(R3+C3)*Y3loan; C3=MAJ(acc2,E2,C2); C4=(~final3)*Y3loan',
        'guard_rows':rows,'expected_mean_delta':'-15/16','emitted_CCX_delta':2,
        'expected_build_probabilities':{'C4':'1/2','C3':'1/4','TT':'13/16','C6_factor':'1/2'},
        'schedule':'DelayC6 repair untilT3 measured; one sharedtempq carriesC4 ifm6, otherwiseC3 ifm3. C6 correction readsC4 onlyifm6. T3 usesexistingC4/TT identity ifm6, directCZ(R3+C3,Y3loan) otherwise. Measuresharedtemp andcorrecteach mutuallyexclusive producer underits storedguard. TT builds onlyfor(m6*m3),mY5,mY3.',
        'ownership':'AllE andrebuiltC2 retained; sharedtemp producerbranches mutuallyexclusive. T3/Y3/C6 correctionoperand values unchangedbeforetheir phaseuse. Fin3first; fin4/top1 requirescorrespondingall18producerdomain test.',
        'limits':'Guard/sourcealgebra only, no physicalnativeclaim. No full score.', 'qualified_score':None}
(here/'actual-adaptive-guards-v7.json').write_bytes((json.dumps(record,indent=2)+'\n').encode());print(json.dumps({'status':record['status'],'prospective_mean_delta':str(delta)}))
