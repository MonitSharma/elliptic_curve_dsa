from pathlib import Path
r=Path(__file__).resolve().parent;s=(r.parent/'breakthrough-width-correctness-20261020/run.py').read_text();s=s.replace("candidate=ws/'breakthrough-reverse-budget-20261020'","candidate=ws/'breakthrough-wide-loan-policy-20261020'")
a="paths={name:candidate/f'cap{name[3:]}/ops.bin'for name in f['streams']}";b="paths={name:Path(f['paths'][name])for name in f['streams']}";assert s.count(a)==1;s=s.replace(a,b).replace("records['raw1234']","records['public1863']").replace("name=='raw1234'","name=='public1863'");(r/'run.py').write_bytes(s.encode())
