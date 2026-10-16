from pathlib import Path
root=Path(__file__).resolve().parent
code=(root/'summarize_compact11_census.py').read_text().replace('compact11-frozen-census-20261016','product25-frozen-census-v2-20261016').replace('product-compact11-frozen-20261016','product25-frozen-20261016').replace('compact11-census-summary.json','product25-census-summary.json')
exec(compile(code,str(root/'summarize_compact11_census.py'),'exec'))
