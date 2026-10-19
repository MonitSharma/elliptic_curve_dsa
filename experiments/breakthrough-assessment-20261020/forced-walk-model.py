"""Classical feasibility of one-bit odd-preserving walk transcripts.

No circuit, payload, finite envelope, phase or resource record is produced.
Fixed diagnostics compare decision bits per reduction, not fitted truncations.
"""
import hashlib,json,math,statistics,time
from pathlib import Path
from datetime import datetime,timezone
from importlib.util import spec_from_file_location,module_from_spec

r=Path(__file__).resolve().parent
spec=spec_from_file_location('history',r/'history-model.py');model=module_from_spec(spec);spec.loader.exec_module(model)
P=(1<<256)-(1<<32)-977
LABEL=b'breakthrough-forcedwalk-integer-v1'
SAMPLES=4096

def seed(d,p):
    assert p%4==3
    a=d if d&1 else d-p
    b=(a+(p if a%4==3 else -p))//2
    assert a&1 and b&1
    return a,b

def run(d,p,kind):
    a,b=seed(d,p);target=0;steps=0;history=0;peak=abs(a).bit_length()+abs(b).bit_length()+2
    if kind.startswith('forced'):
        block=int(kind[-1])
    else:block=0
    for tick in range(10000):
        if abs(a)==abs(b):
            assert abs(a)==math.gcd(d,p)
            return {'ticks':tick,'half_steps':steps,'history_bits':history,'peak_history_plus_signed_rails':peak}
        t,source=(a,b)if target==0 else(b,a)
        if block:
            for _ in range(block):
                t,_=model.forced(t,source);steps+=1;history+=1
        else:
            t,_=model.forced(t,source);t,_=model.forced(t,source);steps+=2
            allow=abs(t)>4*abs(source)
            out,_,k1,k2=model.bits_choice(t,source,allow)
            t=out;steps+=1+k1+2*k2;history+=5
        if target==0:a=t
        else:b=t
        peak=max(peak,history+abs(a).bit_length()+abs(b).bit_length()+2)
        target^=1
    raise RuntimeError(('Nontermination in declared model bound',d,p,kind,a,b))

def main():
    out={'status':'INTEGER_FEASIBILITY_ONLY_NOT_A_QUANTUM_RESOURCE_ESTIMATE','label':LABEL.decode(),'samples':SAMPLES,
         'started_at_utc':datetime.now(timezone.utc).isoformat(),'variants':{},
         'limitations':['All bits counted are classical model dimensions, not physical qubits.','No payload arithmetic, quantum phase, cleanup, endpoint circuit or fixed iteration circuit exists.','Sample maxima must never be installed as new approximate circuit cuts.','Full-precision comparison differs from the incumbent window rule.']}
    inputs=[1+int.from_bytes(hashlib.shake_256(LABEL+i.to_bytes(8,'little')).digest(32),'little')%(P-1)for i in range(SAMPLES)]
    for kind in ['forced1','forced2','forced3','forced4','adaptive_generic']:
        start=time.time()
        small=0
        for p in [7,11,19,23,31,43,127,251]:
            for d in range(1,p):run(d,p,kind);small+=1
        rows=[run(d,P,kind)for d in inputs]
        summary={key:{'mean':statistics.mean(x[key]for x in rows),'max':max(x[key]for x in rows),
                      'min':min(x[key]for x in rows),'stdev':statistics.stdev(x[key]for x in rows)}
                 for key in rows[0]}
        out['variants'][kind]={'small_exhaustive_inputs':small,'seconds':time.time()-start,'metrics':summary}
        (r/'FORCED-WALK-PROGRESS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
        print(kind,json.dumps(summary),flush=True)
    out['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    (r/'FORCED-WALK-MODEL.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
