"""Archive the source-only observer, including its failed first launcher."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'dynamic-pool-20261015/collect.py').read_text()
s=s.replace("['control.exit','wide.exit']","['origin.exit']").replace("root/'control-equality.log'","root/'origin-equality.log'").replace("['control-b3','wide-b3']","['origin-b3']")
a=s.index('fixed_sets=');b=s.index("receipt={'collected_at':",a)
s=s[:a]+"fixed_sets={}\n"+s[b:]
s=s.replace("'status':'terminal diagnostic research; qualification incomplete'","'status':'terminal gate-inert source observation; not a candidate benchmark'")
(root/'collect.py').write_text(s)
(root/'verify-local.py').write_text((root.parent/'dynamic-pool-20261015/verify-local.py').read_text())
