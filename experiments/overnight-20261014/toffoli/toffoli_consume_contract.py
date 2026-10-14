"""Expose a new constructor/consumer value contract after two ladder bits.

The actual low-bit writes and phase cleanup must still be implemented together;
this produces exact truth targets and bounds, not an arithmetic replacement.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure,load

HERE=Path(__file__).parent
old=json.loads(HERE.joinpath("constructor-netlist.json").read_text())
def moved(mask):return (mask&((1<<15)-1))|((mask>>15)<<17)
gates=[dict(name=g["name"],a=moved(g["a"]),b=moved(g["b"])) for g in old["gates"]]
out=[moved(v) for v in old["outputs"]]
c6=out[27]
gates.append({"name":"consume_carry7","a":(1<<15)^c6,"b":out[2]^c6})
c7=(1<<48)^c6
gates.append({"name":"consume_carry8","a":(1<<16)^c7,"b":out[3]^c7})
c8=(1<<49)^c7
result6=(1<<15)^out[2]^c6
result7=(1<<16)^out[3]^c7
net=dict(old,input_count=16,input_order=old["input_order"]+",acc6,acc7",gates=gates,
         outputs=out[4:21]+out[21:27]+[result6,result7,c8],
         outputs_order="Q4,Q5,U0..U6,sign,H0..H6,low_result0..low_result7,carry8",
         limits="Value-only joint constructor+first2carry stages. Does not establish retained-wire cleanup or phase equivalence.")
HERE.joinpath("consume-two-netlist.json").write_bytes((json.dumps(net,indent=2)+"\n").encode())
raw,targets,values=load(net)
for r in range(1<<16):
    acc=(r&63)|((r>>14&3)<<6)
    ev,nm,k1,k2=r>>6&7,r>>9&7,r>>12&1,r>>13&1
    c3=int((acc&7)+ev>=8);c4=(acc>>3&1)&c3
    q=nm+(acc&7);a4=q&1;a5=(q^(q>>1))&1;a,z=acc>>4&1,acc>>5&1
    c5=(a&a4)|(a&c4)|(a4&c4)
    y3=(k1|k2)&((acc>>3&1)^c3);y4=k2&(a^c4^a4);y5=(k1&k2)&(z^c5^a5)
    k=q+8*(y3+2*y4+4*y5-c3)
    low=(acc+ev+(-(2**32+976)*k&255))
    assert sum((v>>r&1)<<i for i,v in enumerate(targets[17:25]))==low%256
    assert targets[25]>>r&1==low//256
closure_result=closure(raw,targets)
report={"source_cases":1<<16,"arithmetic_mismatches":0,"input_span_rank":len(Space(raw).values),
        "value_output_span_rank":len(Space(raw+targets).values),"source_ANDs":len(gates),
        "rank_AND_lower_bound":len(Space(raw+targets).values)-len(Space(raw).values),
        "closure":closure_result,"netlist_sha256":hashlib.sha256(HERE.joinpath("consume-two-netlist.json").read_bytes()).hexdigest(),
        "status":"new value-interface lead; no native replacement or scored saving"}
HERE.joinpath("consume-two-analysis.json").write_bytes((json.dumps(report,indent=2)+"\n").encode())
print(json.dumps({k:v for k,v in report.items() if k!="closure"},indent=2))
print({"closure_status":closure_result["status"],"computed_ANDs":len(closure_result["gates"])})
