from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'run-product25-census-v2.sh').read_text().replace('product25-frozen-census-v2-20261016','product25-frozen-census-v3-20261016').replace('/simd-census-20261016/bin/simd_census_v1','/simd-census-v2-20261016/bin/simd_census_v2').replace('49d99d2bf380b628550c3ed979b5bf2adfc1a962fb6fd00a5df267cde853f554','790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66').replace('summarize_product25_census_v2.py','summarize_product25_census_v3.py')
(r/'run-product25-census-v3.sh').write_text(s,newline='\n')
(r/'summarize_product25_census_v3.py').write_text((r/'summarize_product25_census_v2.py').read_text().replace('product25-frozen-census-v2-20261016','product25-frozen-census-v3-20261016'),newline='\n')
