from pathlib import Path
a=Path(__file__).parent;old=a.parent/'breakthrough-current-product-census-anf-shadow-20261021'
(old/'STATUS.md').write_text('# Compile-only failure preserved\n\nRust could not infer the parsed scalar type inside assert_eq. No native test, point replay, census gate or nonce screen ran. V2 uses a generic scalar parser with the expected scalar argument determining the exact type; parse failures still panic. Original frozen source and compile logs are preserved. ANF/cache/source unchanged.\n')
s=(a/'prepare-census-anf-shadow.py').read_text().replace('breakthrough-current-product-census-anf-shadow-20261021','breakthrough-current-product-census-anf-shadow-v2-20261021')
exec(compile(s,str(a/'prepare-census-anf-shadow.py'),'exec'))
