"""Review composed seed evidence and independently checked proof bindings."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
root=Path(__file__).resolve().parents[2]/'experiments'
spec=[('current-value-attribution-20261016/seed-diagnosis-v1.tar.gz','3ae03610ff43dc3473630ebb6cf095de949ee007df6425f2a955c1c171d886a8',66),('prefilter-20261015/evidence-seed-independent-review-v2.tar.gz','4f05ba7942228e2183d2208e26fff0582a12a0e4207f6d7802577255a34e6d11',29)]
records=[]
for rel,sha,count in spec:
 p=root/rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
 with tarfile.open(p) as t:
  names=t.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
  assert all(m.isfile() or m.isdir() for m in t.getmembers())
  mn=next(n for n in names if n.endswith('MANIFEST.json'));prefix=mn[:-len('MANIFEST.json')];read=lambda n:t.extractfile(prefix+n).read()
  m=json.loads(read('MANIFEST.json'));files=m['files'];assert len(files)==count
  if isinstance(files,list):items=[(v['path'],v) for v in files]
  else:items=list(files.items())
  for n,v in items:
   raw=read(n);assert hashlib.sha256(raw).hexdigest()==v['sha256'],n
   if 'bytes' in v:assert len(raw)==v['bytes'],n
  if count==66:
   base=json.loads(read('BASE-PINS.json'))
   for name,h in base['depends_on'].items():assert hashlib.sha256((root/'current-value-attribution-20261016'/name).read_bytes()).hexdigest()==h
   before=json.loads(read('seed-prefix-pinned-v1/before.json'));assert before==json.loads(read('seed-prefix-pinned-v1/after.json'))
   assert before['/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
   zero=json.loads(read('seed-prefix-pinned-v1/replay.log'));assert zero['at']==618858 and zero['q']==list(range(1106,1154)) and zero['exact_zero']==[True]*48
   assert zero['all_original_ops_no_rewrites'] and zero['all_symbolic_ABI_inputs_and_MR']
   bdd=json.loads(read('seed-bdd-contract.json'));original=bdd['original_source']
   assert original['all256_target_bits_match_finite53_formula'] and original['all_scratch_restored_zero'] and original['phase_exact_zero'] and original['MR_draws']==96
   assert not bdd['current_inherited_negative']['all256_target_bits_match_finite53_formula']
   predicate=json.loads(read('seed-entry-predicate-v1.json'));assert predicate['predicate']=='D=(A odd) AND ((A mod 2^32)<977)' and predicate['inherited_phase']=='D * MR[20]'
   diff=json.loads(read('seed-region-diff.json'));assert len(diff['changes'])==1 and diff['raw_ops']==diff['actual_ops']==933 and diff['changes'][0]['actual_begin']==619000
   lines=read('seed-attribution.log').decode().splitlines();batch=[s for s in lines if s.startswith('ATTR_BATCH ')];shots=[s for s in lines if s.startswith('PAY_SHOT ')]
   assert len(batch)==413 and len(shots)==431 and all('full64q_b_phase_T_equal=true' in s and 'original_census_flags_reproduced=true' in s for s in batch)
   assert all('observer_equal=true' in s for s in shots)
   assert read('seed-attribution-stream-before.sha256')==read('seed-attribution-stream-after.sha256')
  else:
   assert hashlib.sha256(read('REVIEW.json')).hexdigest()=='bf7c0204bb4a22b2501e0598e1677bcaa41d86a082ee32c28f451fb68775370b'
  records.append(dict(archive=rel,sha256=sha,verified_members=count))
out=dict(status='SEED_DIAGNOSIS_HASHES_COMPLETE_REPLAY_CLEAN_PREFIX_AND_INDEPENDENT_REVIEW_BOUND',archives=records,helper_domain='Arbitrary256bit target and96MR with48scratch zero; actual original prefix proves those48 zeros.',source_family='All dropped controls in all mod_halve_pm helpers, one site; native/fresh qualification remains separate.',not_a_global_correctness_or_resource_record=True)
(root/'current-value-attribution-20261016/ROOT_SEED_DIAGNOSIS_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
