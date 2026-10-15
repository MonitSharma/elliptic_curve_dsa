"""Preserve both comparison candidates, including any construction failure."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'dynamic-pool-20261015/collect.py').read_text()
a=s.index('for name in [');b=s.index('for p in sorted(root.iterdir()):',a)
s=s[:a]+"for name in ['narrow.exit','wide.exit']:assert name in exits,exits\n"+s[b:]
s=s.replace("['control-b3','wide-b3']","['narrow-b3','wide-b3']")
s=s.replace("'HEO_TOTAL'","'HEO_TOTAL','Y15_UNSEEDED'")
a=s.index('fixed_sets=');b=s.index("receipt={'collected_at':",a)
s=s[:a]+"fixed_sets={mode:{family:sorted(map(int,re.findall(r'FINAL_BAD shot=(\\d+)',(root/(mode+'-'+family+'.log')).read_text()))) for family in ['independent','structured','candidate'] if (root/(mode+'-'+family+'.log')).exists()} for mode in ['narrow','wide']}\n"+s[b:]
s=s.replace("'source_trace_byte_identical':True","'source_trace_byte_identical':False")
s=s.replace('Allocator tests establish bookkeeping invariants, not quantum cleanliness; fixed replay checks dirty ancillas separately.','Y15 source predictors are removed uniformly; truncated seedless comparisons and reconstructed carry chains remain approximate.')
(root/'collect.py').write_text(s)
(root/'verify-local.py').write_text((root.parent/'dynamic-pool-20261015/verify-local.py').read_text())
