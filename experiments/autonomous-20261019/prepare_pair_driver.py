"""Prepare serial controls, complete baseline reproduction and one fixed scan."""
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-pair-witness-20261020'
assert not (r/'run.py').exists()
s=(ws/'product-anf-witness-20261019/run.py').read_text()
s=s.replace("old=ws/'product-anf256-20261019'","old=ws/'product-copy-cache-witness-20261020'")
s=s.replace("inp=ws/'product-classical-closure-20261019/input.ops.bin'","inp=ws/'product-copy-cache-20261019/copy-cache.ops.bin'").replace('17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7','53bb99238f013b7308b88e26d063d6d9ec3b364d1f0e2b2501b6abe368a75fb1')
s=s.replace("ANF_WITNESSES='1',OMP_NUM_THREADS", "ANF_PAIR_WITNESSES='0',ANF_WITNESSES='1',OMP_NUM_THREADS")
s=s.replace('2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265','d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5')
s=s.replace("dict(os.environ,ANF_WITNESSES='0')","dict(os.environ,ANF_PAIR_WITNESSES='0')")
s=s.replace("'witness.log')","'witness.log',dict(os.environ,ANF_PAIR_WITNESSES='1'))")
s=s.replace('EXACT_CURRENT_WIRE_ANF_WITNESS_SOURCE_SCREEN_COMPLETED','EXACT_TWO_WIRE_XOR_PRODUCT_SOURCE_SCREEN_COMPLETED')
s=s.replace("'current_wire_witness_sites':sum(x.get('kind')=='exact_current_wire_product'", "'pair_witness_sites':sum(x.get('kind')=='exact_two_wire_xor_product'")
s=s.replace("'witness_mode':(env or os.environ).get('ANF_WITNESSES')", "'pair_witness_mode':(env or os.environ).get('ANF_PAIR_WITNESSES')")
(r/'run.py').write_text(s,newline='\n')
s=(ws/'product-copy-cache-20261019/run.sh').read_text().replace('product-copy-cache-20261019','product-pair-witness-20261020');(r/'run.sh').write_text(s,newline='\n')
s=(ws/'product-copy-cache-20261019/launch.py').read_text().replace('product-anf-witness-20261019','product-copy-cache-witness-20261020').replace('Local reversible copy-cache job','Local exact two-wire XOR product job')
(r/'launch.py').write_text(s,newline='\n')
print('Prepared fixed pair driver; launch refuses until current local source screen exits0')
