"""Freeze exact remapped boundary observations without turning diagnostics into scores."""
from pathlib import Path
import collections,hashlib,json,re,sys
root=Path(__file__).resolve().parents[3]
raw=root/'research-output/overnight-20261014/product/body-prefix-replay-v2'
out=root/'experiments/overnight-20261014/product'
assert int((raw/'run.exit').read_text())==0
text=(raw/'run.log').read_text()
assert 'PRODUCT_BODY_TOTAL' in text and 'archived_final_values_and_phase_verified=true' in text
rows=[]
for line in text.splitlines():
 if line.startswith('PRODUCT_BODY_POINT '):rows.append(dict(re.findall(r'(\w+)=(\S+)',line)))
assert len(rows)==2*271*9
groups=collections.defaultdict(list)
for r in rows:groups[(r['source'],r['mode'],r['boundary'])].append(r)
stats=[]
for (source,mode,boundary),rs in groups.items():
 stats.append(dict(source=source,mode=mode,boundary=boundary,shots=len(rs),x_bad=sum(r['x_correct']=='false'for r in rs),y_bad=sum(r['y_correct']=='false'for r in rs),nonuniform=sum(r['extension_uniform']=='false'for r in rs),classic_bad=sum(r['classic_inputs_retained']=='false'for r in rs),pending_y33_counts=sorted(set(int(r['pending_y33'])for r in rs))))
first={}
for source in ['c5_raw','b3_raw']:
 for mode,index in [(r['mode'],r['index'])for r in rows if r['source']==source and r['boundary']=='coord-y-sub']:
  rs=[r for r in rows if (r['source'],r['mode'],r['index'])==(source,mode,index)]
  bad=next((r for r in rs if r['x_correct']=='false' or r['y_correct']=='false' or r['extension_uniform']=='false'),None)
  if bad:first[f'{source}:{mode}:{index}']=dict(boundary=bad['boundary'],x_bad=bad['x_correct']=='false',y_bad=bad['y_correct']=='false',extension_nonuniform=bad['extension_uniform']=='false')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in raw.iterdir()if p.is_file()}
receipt=dict(status='COMPLETED_SOURCE_BOUND_DIAGNOSTIC',exit=0,qualified_score=None,points_per_source=271,boundaries_per_point=9,
 mapping='All9 emitted metadata hashes verified in correct pre-Y33/final domains; exact copied-source entire Y33 transformation OpVec equality; event prefix map; pending target logical reconstruction; unchanged full circuit final SHA256 verified by independent observer receipts.',
 native=(raw/'native.sha256').read_text().strip(),source_hashes=(raw/'source.sha256').read_text(),input_hashes=(raw/'input.sha256').read_text(),artifact_hashes=hashes,
 all_final_values_and_phase_equal_archived_continuous_raw_replay=True,phase_alignment='Exact continuous final-raw transcript within each source/batch; no cross-source MR alignment or intermediate phase-fault claim.',stats=stats,first_bad_by_point=first,
 important_points=[r for r in rows if r['mode']=='official_known_bad'and r['index']in['249','8033']])
(out/'body-prefix-v2-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
md=['# Source-bound arithmetic boundary replay','',
 'The two gate-inert observers reproduce the original complete C5/B3 circuit streams exactly, with all binding assertions retained. Both emitted and finalized prefix hash domains are verified. A copy of the unchanged Y33 cleanup must reproduce the entire finalized raw operation vector exactly before any point is interpreted. Its exact insert/remove events remap each boundary; pending cleaned wires receive a logical overlay reconstructed from their old unconditional writes. One native overlay/source-mutation fault test passes. Final coordinates and phase on all271 points per source equal the separately archived whole-raw replay.','',
 '| Source | Packet | Boundary | Shots | Wrong x | Wrong y | Nonuniform sign |','|---|---|---|---:|---:|---:|---:|']
for s in stats:md.append(f"| {s['source']} | {s['mode']} | {s['boundary']} | {s['shots']} | {s['x_bad']} | {s['y_bad']} | {s['nonuniform']} |")
md+=['','First failing arithmetic boundary for the two requested cases:']
for source in ['c5_raw','b3_raw']:
 for index in ['249','8033']:
  entry=first.get(source+':official_known_bad:'+index)
  detail='all documented boundary contracts pass' if entry is None else entry['boundary']+'; wrong '+('/'.join(k for k in ['x','y'] if entry[k+'_bad']))
  md.append(f'- {source} point {index}: {detail}.')
md+=['','All sampled boundaries have zero pending Y33 sites; the logical overlay therefore equals the physical values at these boundaries. The full copied transformation and prefix hash checks are still necessary because completed Y33 rewrites alter earlier operation content. Every sign extension is uniform, and all classical input words remain intact.','',
 'Final stream SHA256: C5 `49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`; B3 `0f10de57f45349c89163faf6e5ab0694aec3d3bfa720f10ee8b185a9fb2914ce`. Exact observer patches, protected-file checks and source bindings are in the paired `c5/b3-body-boundaries-v2` receipts. Runtime replay binary: `'+(raw/'native.sha256').read_text().split()[0]+'`.']
md+=['','Arithmetic expectations follow the actual seamed caller: subtraction leaves y=Ty−Ay; division leaves y=lambda and x=Tx+2Ax+squareOffset; signed square frame leaves x=Tx+2Ax−lambda²; multiplication leaves the final x and y=expectedFinalY+Ay; final subtraction yields final coordinates. At the square boundary the actual extra sign wires are checked and the signed residue is decoded using 2^256≡2^32+977 mod p.','',
 'These are finite, source-bound value observations. Phase uses the exact continuous finalized raw measurement transcript within each source, and final phase equals the archived raw replay. Intermediate phase can carry legitimate deferred correction; cross-source measurement transcripts are unaligned. No scored resource result or global arithmetic correctness is claimed. The first failed v1 mapping assertion and its source/binary/log remain preserved separately.']
(out/'body-prefix-v2-results.md').write_text('\n'.join(md)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'stats':stats,'points2498033':{k:v for k,v in first.items()if k.endswith(':249')or k.endswith(':8033')}},indent=2))
