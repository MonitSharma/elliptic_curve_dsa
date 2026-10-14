"""Exact source-width finite missing-borrow certificates; no candidate modification."""
from pathlib import Path
import hashlib,json
folder=Path(__file__).parent
analysis=json.loads((folder/'fold75-analysis.json').read_text())
certificates=[]
for r in analysis['proofs']:
 x=int(r['actual_unsigned_add2'],16)%(2**256);w=int(r['expected_unrotated_word'],16);actual=int(r['actual_postfold_word'],16)
 # Actual unchanged source policies: C5 forwardprefix<=99, B3<=55, otherwise56.
 mw=57 if r['tick'] <= (99 if r['source']=='c5_raw' else 55) else 56
 correction=w-x
 low=x%(2**mw);total=low+correction
 modular=(x//2**mw)*2**mw+(total%(2**mw))
 assert modular==actual,(r['source'],r['index'],r['tick'],hex(modular),hex(actual))
 assert r['producer_exact']and r['source_preserved_all']
 if not r['postfold_exact']:
  assert total<0 and actual-w==2**mw and r['close_delta']==2**mw
  certificates.append(dict(source=r['source'],mode=r['mode'],index=r['index'],tick=r['tick'],actual_width=mw,rotation=r['rotation_shift'],
   logical_input_word=hex(x),input_low=hex(low),exact_correction=correction,exact_low_sum=total,borrow_out=True,
   correct_full_word=hex(w),modulo_window_word=hex(actual),missing_borrow_delta=2**mw,after_rotation_delta=2**(mw-r['rotation_shift']),
   low_bits_exact=actual%(2**mw)==w%(2**mw),high_word_unchanged=actual//2**mw==x//2**mw))
doc=dict(status='EXACT_FINITE_SOURCE_WIDTH_BORROW_CERTIFICATE',qualified_score=None,all_cases_match_exact_modulo_source_window=64,
 source_rules={'c5':'y15_onefold.rs fold_window: forward tick<=99 width57, otherwise56','b3':'y15_onefold.rs fold_window: forward tick<=55 width57, otherwise56'},
 previous_assumption_corrected='Earlier direct message assumed bothsource tick75 width56. Source audit disproves that: C5tick75 width57. No report or score was based on that assumption.',
 explanation='All64 exact reconstructed unsigned add2 producers match independently computed integer sums. Native postfold equals the correct field/rotation word modulo the source window while retaining the old high word. Three cases need a borrow out of that window; it is omitted, giving exactly +2^56 before rotation. Ripple closure preserves the error. Generic lower-window fold contracts remain satisfied; whole-body field contract fails.',
 analysis_sha256=hashlib.sha256((folder/'fold75-analysis.json').read_bytes()).hexdigest(),certificates=certificates,
 scope='Finite first cause certificates on original bound streams, no universal repair or resource score. A larger fixed window reduces but cannot eliminate every possible carry/borrow overflow. Exact higher-bit propagation needs its own reversible/phase/allocator proof.')
(folder/'fold75-borrow-certificate.json').write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
print(json.dumps(doc,indent=2))
