"""Expose available shift controls at a joint constructor cut."""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location("ctor",HERE/"toffoli_constructor.py")
ctor=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctor)
raw=ctor.ROOT/"research-output/overnight-20261014/toffoli/cut-targets.json"
bundles=json.loads(raw.read_text())
model,_=ctor.constructor()
expanded=[]
for index in [0,1,2,3,4,6,10,11,18]:
    v=bundles[index]
    v["input_columns_hex"] += [hex(model.vals[13]),hex(model.vals[14])]
    v["extra_available_inputs"]=["raw12=shift_k1","raw13=shift_k2"]
    v["input_rank_including_constant"]=ctor.fc.rank([int(x,16) for x in v["input_columns_hex"]])
    expanded.append(v)
destination=ctor.ROOT/"research-output/overnight-20261014/toffoli/cut-shift-targets.json"
destination.write_text(json.dumps(expanded)+"\n")
print([(v["cut"]["first"],v["cut"]["last"],v["input_rank_including_constant"]) for v in expanded])
