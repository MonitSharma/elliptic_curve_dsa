"""Materialize terminal evidence collection for the control and wrapper."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'y15-unseeded-20261015/collect.py').read_text().replace('narrow','control').replace('wide','wrapped')
s=s.replace("['control.exit','wrapped.exit']","['control.exit','wrapped.exit','observer.exit']").replace("['control-b3','wrapped-b3']","['control-b3','wrapped-b3','observer-b3']")
s=s.replace("'Y15_UNSEEDED'","'Y15_UNSEEDED','ZERO_EQUALITY_PROOF','PAYLOAD_INTERFACE','PAYLOAD_OBSERVATION'")
s=s.replace('Y15 source predictors are removed uniformly; truncated seedless comparisons and reconstructed carry chains remain approximate.','The zero helper has finite all-measurement tests. Full wrapper correctness also requires the actual arithmetic oracle and coordinate/encoding contracts; those are evaluated separately.')
(root/'collect.py').write_text(s)
(root/'verify-local.py').write_text((root.parent/'y15-unseeded-20261015/verify-local.py').read_text())
