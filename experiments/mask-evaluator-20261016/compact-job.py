from pathlib import Path
import runpy,sys
root=Path(__file__).resolve().parent
prior=root/'ACTUAL-EXPORT-RESULT.json'
saved=root/'EXPANDED-V1-RESULT.json'
assert prior.exists() and not saved.exists()
saved.write_bytes(prior.read_bytes())
sys.argv=[str(root/'verify-export.py'),'/home/hclau/ecdsa_research/prefilter-20261015/evidence/mr-mask-tip-v3.bin','560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d']
runpy.run_path(sys.argv[0],run_name='__main__')
(root/'COMPACT-V3-RESULT.json').write_bytes(prior.read_bytes())
prior.write_bytes(saved.read_bytes())
