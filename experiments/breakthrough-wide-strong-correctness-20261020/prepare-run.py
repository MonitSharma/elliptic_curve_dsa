from pathlib import Path
r=Path(__file__).resolve().parent;s=(r.parent/'breakthrough-wide-correctness-20261020/run.py').read_text();a="candidate=ws/'breakthrough-wide-loan-policy-20261020'";assert s.count(a)==1;s=s.replace(a,"candidate=ws/'breakthrough-wide-stronger-compare-20261020'");(r/'run.py').write_bytes(s.encode())
