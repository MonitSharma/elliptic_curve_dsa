"""Finite source-bound selector/donor proof, separate from curve admission."""
from pathlib import Path
import hashlib,json,re,sys
source,out=map(Path,sys.argv[1:3]);text=source.read_text()
body=text[text.index('fn size_partition('):text.index('pub(crate) fn stage1_v_compact_partitioned')]
rows=re.findall(r'&\[(\([0-9].*?)\]',body,re.S);assert len(rows)==2
cubes=[[(int(a),int(b))for a,b in re.findall(r'\((\d+),(\d+)\)',row)]for row in rows]
small,large=cubes
match=lambda v,c:sum((v&m)==b for m,b in c)
for sy in range(1,129):
    assert match(sy&127,small)==int(sy<=96)
    assert match(sy&127,large)==int(sy>=97)
for sy in range(256):
    assert match(sy&127,small)<=1 and match(sy&127,large)<=1
    assert match(sy&127,small)+match(sy&127,large)<=1
assert 'let high6=[(63usize,37usize),(62,38),(56,40),(48,48)]'in text
assert 'literals.extend((0..6).map(|i|(sz[i],i!=5)))'in text
assert 'c.extend((0..6).map(|i|(sz[i],i!=5)))'in text
high6=[(63,37),(62,38),(56,40),(48,48)];high7=[(32,0),(63,32)]
for size in range(101,161):
    assert match(size&63,high6)==(size>>6&1)
    assert match(size&63,high7)==(size>>7&1)
assert len({size&63 for size in range(101,161)})==60
for low in range(64):assert match(low,high6)<=1 and match(low,high7)<=1
maxpark=0
for sy in range(1,97):
    for bit in range(24):maxpark=max(maxpark,sy+bit);assert sy+bit<120
states=0
for sy in range(97,129):
    for size in range(101,258-sy):
        assert size<=160 and match(size&63,high6)==(size>>6&1)and match(size&63,high7)==(size>>7&1);states+=1
report=dict(scope='Source-bound finite predicates only; determinant and source lower-envelope admission are separate assumptions, not full circuit proof',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),SY_admitted=128,SY_full_words_checked=256,small_cubes=small,large_cubes=large,SZ_admitted_sizes_checked=60,SZ_low_words_checked=64,SZ_SY_admitted_pairs_checked=states,max_parked_index_small_SY_QB24=maxpark,Q120_127_clean_under_admitted_bounds=True,high6_cubes=high6,high7_cubes=high7,inactive_case='Disjoint selectors may alias high SY bits; act separately prevents window changes. Care/normalization inverse restores arbitrary inactive words, as native unitary fixtures check.',status='pass')
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
