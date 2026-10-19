from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'activate_finalizer_v2.py').read_text()
s=s.replace("old=ws/'classical9-final-20261019';new=ws/'classical9-final-v2-20261019'","old=ws/'classical9-final-v2-20261019';new=ws/'classical9-final-v3-20261020'")
s=s.replace('preflight_v14.py','preflight_v15.py').replace('FINALIZER-V2-TRANSITION.json','FINALIZER-V3-TRANSITION.json')
s=s.replace("assert sha(ws/'autonomous-20261019/preflight_v15.py')==ready['profile_sha256']","assert sha(ws/'autonomous-20261019/preflight_v15.py')==ready['profile_sha256']\nassert sha(ws/'autonomous-20261019/resource_registry.py')==ready['profile_helper_sha256']")
s=s.replace('New explicit registry permits forthcoming source12 runtime validation while retaining the entire frozen source9 search/finalization path.','Source-hashed dynamic descriptors permit future native/proof jobs without changing any running profile, circuit, search or scorer.')
p=r/'activate_finalizer_v3.py';assert not p.exists();p.write_text(s,newline='\n')
