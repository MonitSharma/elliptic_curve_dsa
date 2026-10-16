from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent;d=r.parent/'guard-fused-20261016';assert not d.exists();d.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(d/'compile-mask-fused.py').write_bytes((r/'compile-mask-fused.py').read_bytes())
s=(r/'verify-mask-fused.py').read_text()
s=s.replace("r=Path(__file__).parent;prefix=r/'evidence/mr-mask-tip-v3-fused'","r=Path(__file__).parent;prefix=r/'guard-fused'")
s=s.replace("source=(r/'evidence/mr-mask-tip-v3.bin').read_bytes()","source=(r/'guard512.bin').read_bytes()")
s=s.replace("(r/'evidence/mask-fused-verification.json')","(r/'whole-plan-verification.json')")
(d/'verify-mask-fused.py').write_bytes(s.encode())
(d/'DECLARATION.json').write_bytes((json.dumps({'status':'COMPONENT_ONLY_NO_RUNTIME_OR_OPERATIONAL_CHANGES','original_guard_sha256':'355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3','wrapper':'Same MRMASK01 nodes and1024ports, repeat sole rawGroot512times; explicit lineage verified before compilation.','compiler_unchanged_sha256':sha(r/'compile-mask-fused.py'),'original_verifier_sha256':sha(r/'verify-mask-fused.py'),'verifier_only_changes':'Source/plan/output path parameters, proof checks unchanged.','kernel_sha256':'dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0','workers':1,'memory_GiB':16,'fixtures':'Existing fixed445 plus existing32audit; deterministic partial subsets only; no new sampled inputs.','raw_polarity':'G=1 excludes transfer; safe=NOT G.','component_timing_only':True},indent=2)+'\n').encode())
print(d)
