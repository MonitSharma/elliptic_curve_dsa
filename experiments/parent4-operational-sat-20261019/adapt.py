from pathlib import Path
r=Path(__file__).resolve().parent
old='268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d'
new='9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'
p=r/'search.rs';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
p=r/'coordinator.py';s=p.read_text();needle="root.parent/'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin'";assert s.count(needle)==1;s=s.replace(needle,"root.parent/'product-pareto-20261019/candidate-parent4/ops.bin'");p.write_text(s)
p=r/'control.py';s=p.read_text();s=s.replace('ws / "product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin"','ws / "product-pareto-20261019/candidate-parent4/ops.bin"')
s=s.replace('ws / "product67-filter-20261016/baseline-0.jsonl"','ws / "product-parent-sat-20261019/parent4-filter/baseline-0.jsonl"')
s=s.replace('"54db817249a41619adb3b4f92bc49fc3bac62a36fc27580749931d158bdf4fb3"','json.loads(acc.read_text())["qualified_prefix_rows_sha256"]')
s=s.replace('qualified PLAIN67 rows','qualified parent4 rows').replace("product67-filter's","parent4-filter's")
p.write_text(s)
