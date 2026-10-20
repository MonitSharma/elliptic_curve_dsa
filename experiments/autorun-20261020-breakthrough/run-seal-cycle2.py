import subprocess
from pathlib import Path
ws=Path("/home/hclau/ecdsa_research")
names=['breakthrough-stackv3-width-plan7-range-20261020', 'breakthrough-stackv3-width-plan7-both-20261020', 'breakthrough-stackv3-plan7-both-stats-20261020', 'breakthrough-stackv3-plan7-generic-20261020', 'breakthrough-stackv3-plan7-generic-v2-20261020', 'breakthrough-stackv3-plan7-zero-donors-20261020', 'breakthrough-stackv3-plan7-context-clean-20261020', 'breakthrough-stackv3-plan7-development-20261020', 'breakthrough-classical-width-audit-20261020', 'breakthrough-classical-width-audit-v2-20261020', 'breakthrough-public-e3-context-clean-20261020', 'breakthrough-public-e3-cache-finished-20261020', 'breakthrough-public-e3-cache-finished-v2-20261020', 'breakthrough-public-e3-cache-development-20261020', 'breakthrough-public-e3-cache-development-v2-20261020', 'breakthrough-live-products-20261020', 'breakthrough-live-products-v2-20261020', 'breakthrough-live-products-absorption-20261020']
for n in names:
 if not(ws/n/"EVIDENCE-MANIFEST.json").exists():subprocess.run(["python3",str(ws/"breakthrough-sparse-polynomial-20261020/seal-research-cycle2.py"),n],check=True)
