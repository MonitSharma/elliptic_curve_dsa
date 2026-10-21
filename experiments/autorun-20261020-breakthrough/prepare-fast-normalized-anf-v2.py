from pathlib import Path
a=Path(__file__).parent;old=a.parent/'breakthrough-fast-current-product-anf-20261020'
(old/'STATUS.md').write_text('# Pre-test review stopped the first representation prototype\n\nThe inline-constant XOR fast path omitted the term-bound check when adding a nonzero constant to a symbolic polynomial already at8terms. That only retained extra exact information, but did not match the declared unchanged8term policy. No native/input run or result exists. V2 restores the same bound on both constant-XOR branches and removes a tautological preparation assertion; quantum source/cache/fixtures unchanged.\n')
s=(a/'prepare-fast-normalized-anf.py').read_text();s=s.replace('breakthrough-fast-current-product-anf-20261020','breakthrough-fast-current-product-anf-v2-20261020')
needle='if a.terms.is_empty(){let mut result=b.clone();result.c^=a.c;return result;}if b.terms.is_empty(){let mut result=a.clone();result.c^=b.c;return result;}'
assert s.count(needle)==1;s=s.replace(needle,needle.replace('return result;','return self.bound(result);'))
needle=";assert'.0'not in tail.replace('tv.o','').replace('tv.z','')or True";assert s.count(needle)==1;s=s.replace(needle,";assert 'p.0'not in tail and 'Poly('not in tail")
exec(compile(s,str(a/'prepare-fast-normalized-anf.py'),'exec'))
