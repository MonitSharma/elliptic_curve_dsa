"""Export the exact constructor as a compact affine-mask AND netlist."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location("ctor",HERE/"toffoli_constructor.py")
ctor=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctor)
model,targets=ctor.constructor()
def mask(value):
    result=0
    while value:
        v,m=model.pivots[value.bit_length()-1]
        value ^= v
        result ^= m
    return result
gates=[]
for j,(name,a,b,v) in enumerate(model.gates):
    aa,bb=mask(a),mask(b)
    assert aa < 1<<(15+j) and bb < 1<<(15+j)
    gates.append({"name":name,"a":aa,"b":bb})
net={"baseline_revision":"c5bb1ec876db859a3f9f8a9052c140a145df834e",
     "source":"src/point_add/y15_onefold.rs",
     "source_lf_sha256":hashlib.sha256(ctor.SOURCE.read_bytes().replace(b"\r\n",b"\n")).hexdigest(),
     "input_count":14,"input_order":"acc0..acc5,E0..E2,Nm0..Nm2,k1,k2",
     "outputs_order":"Q0..Q5,U0..U6,sign,H0..H6,low_result0..low_result5,carry6",
     "gates":gates,"outputs":[mask(v) for v in targets],
     "limits":"Value constructor only; original carry wires are represented by their underlying AND plus prior affine inputs. Native cleanup must be separately implemented and verified."}
HERE.joinpath("constructor-netlist.json").write_bytes((json.dumps(net,indent=2)+"\n").encode())
print({"AND_count":len(gates),"outputs":len(targets),"source_lf_sha256":net["source_lf_sha256"]})
