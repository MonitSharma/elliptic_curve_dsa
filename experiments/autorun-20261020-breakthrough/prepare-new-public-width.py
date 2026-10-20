from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-stackv3-width-20261020';r.mkdir(exist_ok=True);assert not(r/'PLAN.md').exists()
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('observer/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Native width probe on the new public product source

Parent: official e3b5c51f, Q1234/T756481/product933497554, source88869d8c.
Its exact rail-strip/G6 changes reduce native helper lifetimes. Test whether
1233/1232 budgets now cost less than the previous lineage's expensive width
tradeoff. Preserve all original native arithmetic and existing approximations;
also test the source's documented exact28-bit square witness, strengthening its
inherited21-bit approximation. Do not introduce a weaker check or new cut.

First full public control must exactly reproduce published714c4e4c compressed
stream and every original bound postpass unchanged. Then raw-only fixed cases:
cap1234/witness21, cap1234/witness28, cap1233/witness28, cap1232/witness28.
Only cap/precision parameters and a research raw return change. Original source-
bound passes/tables/assertions remain untouched and unused in raw research.
17 protected files must match the validated challenge harness as Git objects.
Physical Q is measured from full emitted operations; budget is not a width claim.
Keep raw source, source patch, logs, hashes and every failure independently.
Raw/static counts are diagnostics; no final gate, nonce screening or scored
result. Any positive must use self-contained native construction, separately
derived exact passes/leases and sole final gate versus then-current exact parent.
''')
print(r)
