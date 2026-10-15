from pathlib import Path
root=Path(__file__).resolve().parent
source=(root.parent/'scalar-fast-20261015/scalar_batch.c').read_text()
assert source.count('window>20')==1
(root/'scalar_batch.c').write_text(source.replace('window>20','window>22'))
