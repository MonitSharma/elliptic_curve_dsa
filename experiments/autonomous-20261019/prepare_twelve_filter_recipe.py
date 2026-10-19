"""Derive a disabled, source-bound port from the fully qualified nine tool."""
from pathlib import Path
r=Path(__file__).resolve().parent.parent/'product-classical-twelve-filter-20261019';r.mkdir(exist_ok=False)
old=r.parent/'product-classical-nine-filter-20261019'
s=(old/'prepare.py').read_text()
changes={"old=ws/'product-parent-sat-20261019/parent4-filter'":"old=ws/'product-classical-nine-filter-20261019'","n=ws/'product-classical-nine-20261019'":"n=ws/'product-classical-twelve-native-20261019'","proof=ws/'product-classical-nine-proof-20261019'":"proof=ws/'product-classical-twelve-proof-20261019'",'76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1':'17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7','CLASSICAL_NINE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS':'CLASSICAL_TWELVE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS','DISABLED_PARENT4_PIPELINE_QUALIFICATION_PASS':'DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS',"before='9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'":"before='76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1'","('assert_eq!(n,17_889_606)','assert_eq!(n,17_889_627)')":"('assert_eq!(n,17_889_627)','assert_eq!(n,17_889_635)')","product-pareto-20261019/candidate-parent4/ops.bin":"product-classical-nine-20261019/candidate/ops.bin","product-classical-nine-20261019/candidate/ops.bin')\").replace(before,h)":"product-classical-twelve-native-20261019/candidate/ops.bin')\").replace(before,h)",".replace('DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS','DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS')":".replace('DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS','DISABLED_CLASSICAL_TWELVE_PIPELINE_QUALIFICATION_PASS')"}
for a,b in changes.items():
    assert a in s,a;s=s.replace(a,b)
# Keep old-template matching precise: one generated validation input needle,
# one replacement output path, and the new declared native source are distinct.
s=s.replace("'gate_required_before_validation':True", "'gate_required_before_validation':True,'validation_driver_sha256':sha(r/'validate.py')")
(r/'prepare.py').write_text(s,newline='\n')
s=(old/'validate_gate.py').read_text().replace("n=r.parent/'product-classical-nine-20261019'","n=r.parent/'product-classical-twelve-native-20261019'").replace("n/'gate-v2.exit'","n/'gate.exit'")
s=s.replace("assert sha(n/'candidate/ops.bin')==prep['candidate_stream_sha256']==gate['stream_sha256']['candidate']", "assert gate['label']=='pareto-parent4-classical12-gate-20261019-v1' and gate['batches']==262144\nassert sha(r/'validate.py')==prep['validation_driver_sha256']\nassert sha(n/'candidate/ops.bin')==prep['candidate_stream_sha256']==gate['stream_sha256']['candidate']")
(r/'validate_gate.py').write_text(s,newline='\n')
for name in ['run-build.sh','run-qualify.sh']:
    s=(old/name).read_text().replace('product-classical-nine-filter-20261019','product-classical-twelve-filter-20261019').replace('preflight_v9.py','preflight_v14.py')
    if name=='run-build.sh':s=s.replace('python3 prepare.py > prepare.log 2>&1','touch BUILD_ADMITTED\npython3 prepare.py > prepare.log 2>&1')
    (r/name).write_text(s,newline='\n')
