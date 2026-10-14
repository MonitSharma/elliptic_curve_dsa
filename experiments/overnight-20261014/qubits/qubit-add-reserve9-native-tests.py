"""Add native full-column tests, retaining unsupported symbolic evidence.

The old twelve-column symbolic diagnostic remains untouched. These tests
report sampled native phase, not complete independent measurement coefficients.
"""
from pathlib import Path
import re
import sys

dest,fixture_source=map(Path,sys.argv[1:3]);negative='--negative' in sys.argv[3:]
text=fixture_source.joinpath('src/point_add/tests_midg_k24.rs').read_text()
start=text.index('#[test]\nfn k32_exact_column_crossings_boundaries_independent_phase')
test=text[start:]
test=test.replace('k32_exact_column_crossings_boundaries_independent_phase',
                  'reserve7_crossing_3713_negative_native' if negative else 'reserve9_columns_crossing_3713_positive_native')
dx=int('dbc03838c8e3ef33e7b222ced5415f372fbdf32febb8ead3f55c4e58c4f81f55',16)
p=2**256-2**32-977;r,t=[p,dx],[0,1]
while r[-1]:
    q=r[-2]//r[-1];r.append(r[-2]-q*r[-1]);t.append(t[-2]+q*t[-1])
j=60;assert r[j].bit_length()==119 and (r[j-1]//r[j]).bit_length()==19
a=(t[j],r[j-1],r[j],r[j-1].bit_length(),1,0)
z=(t[j+1],r[j+1],r[j],r[j+1].bit_length(),1,0)
case='("shot3713_firstHT",60,['+','.join('"'+format(v,'x')+'"' for v in a[:3])+'],'+','.join(str(v)for v in a[3:])+',['+','.join('"'+format(v,'x')+'"' for v in z[:3])+'],'+','.join(str(v)for v in z[3:])+')'
cases_start=test.index('let cases=&[')+len('let cases=&[')
cases_end=test.index('];let (cols',cases_start)
test=test[:cases_start]+(case if negative else case+','+test[cases_start:cases_end])+test[cases_end:]
test=test.replace('let mut coefficients=0;','')
test=re.sub(r'let\(sym,n\)=symbolic\(&forward,input\.clone\(\)\);assert_eq!\(sym,got\.q\);coefficients\+=n;','',test)
test=re.sub(r'let\(sym,n\)=symbolic\(&inverse,got\.q\);assert_eq!\(sym,input\);coefficients\+=n;','',test)
assert 'symbolic(' not in test
test=test.replace('independent_measurement_coefficients={n}','measurement_coefficients=UNASSESSED')
test=test.replace('independent_measurement_coefficients={coefficients}','measurement_coefficients=UNASSESSED')
test=test.replace('K32_COLUMN_CASE_PASS','RESERVE7_COLUMN_EXPECTED_FAILURE' if negative else 'RESERVE9_COLUMN_CASE_PASS')
test=test.replace('K32_COLUMN_SUITE_PASS','RESERVE7_NEGATIVE_NATIVE_COMPLETE' if negative else 'RESERVE9_NATIVE_SUITE_PASS')
if negative:
    test=test.replace('assert_eq!(got.q,expected,','assert_ne!(got.q,expected,')
    test=test.replace('assert_eq!(got.phase,0,"case {label}");','eprintln!("RESERVE7_NEGATIVE_PHASE mask={:#x}",got.phase);')
    test=test.replace('assert_eq!(back.q,input,"case {label} inverse");assert_eq!(back.phase,0);','eprintln!("RESERVE7_NEGATIVE_INVERSE restores={} phase={:#x}",back.q==input,back.phase);')
path=dest/'src/point_add/tests_midg_k24.rs';assert 'fn reserve9_columns_crossing' not in path.read_text();path.write_text(path.read_text()+test)
