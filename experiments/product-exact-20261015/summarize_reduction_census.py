from pathlib import Path
root=Path(__file__).resolve().parent
code=(root/'summarize_category_census.py').read_text().replace('category-restore-census-20261016','reduction-restore-20261016').replace('product-deletion-restoration-20261016','product-reduction-restoration-20261016').replace('category-census-summary.json','reduction-census-summary.json').replace('complete inherited deletion family','complete inherited reduction family')
exec(compile(code,str(root/'summarize_category_census.py'),'exec'))
