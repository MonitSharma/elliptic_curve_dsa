"""Adapt the previously verified evidence workflow; materialize before upload."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'carry-frame-20261015/collect.py').read_text()
a=s.index('for name in [');b=s.index('for p in sorted(root.iterdir()):',a)
s=s[:a]+'''for name in ['control.exit','wide.exit']:assert exits[name]==0,(name,exits)
assert (root/'control-equality.log').read_text().strip()=='BYTE_IDENTICAL_STREAM=true'
'''+s[b:]
s=s.replace("['origin-b3','state-b3','unseeded-b3','cap1536-b3']","['control-b3','wide-b3']")
s=s.replace("'CARRY_OBSERVATION'","'CARRY_OBSERVATION','Y42_FRESH_RETURNED','HEO_TOTAL'")
a=s.index('fixed_sets=');b=s.index("receipt={'collected_at':",a)
s=s[:a]+'''fixed_sets={family:sorted(map(int,re.findall(r'FINAL_BAD shot=(\\d+)',(root/('wide-'+family+'.log')).read_text()))) for family in ['independent','structured','candidate']}
'''+s[b:]
s=s.replace('Carry snapshot covers one fixed zero-slope input with all-zero measurements; independent-word comparator model does not cover production fold distributions.','Allocator tests establish bookkeeping invariants, not quantum cleanliness; fixed replay checks dirty ancillas separately.')
(root/'collect.py').write_text(s)
(root/'verify-local.py').write_text((root.parent/'carry-frame-20261015/verify-local.py').read_text())
