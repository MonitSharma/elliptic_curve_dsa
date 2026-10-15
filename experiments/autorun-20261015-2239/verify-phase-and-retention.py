"""Independent archive integrity and saved-witness attribution cross-check."""
from pathlib import Path, PurePosixPath
from collections import Counter
import hashlib,json,re,tarfile
root=Path(__file__).resolve().parents[2]/'experiments'
specs=[('current-value-attribution-20261016','phase-attribution-addendum-v2.tar.gz','57f220bd0c5d293940db47fbb700537ba3439a8e5b32076c38fca99b0f4ef108',17),('n2-loan-retention-20261016','source-only-retention-v1.tar.gz','5b8677161c4f40116ac68309201463eed9d580a4327f26b473c8f72e735d875c',362)]
results=[]
for folder,filename,expected,count in specs:
 p=root/folder/filename
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
 with tarfile.open(p) as t:
  names=t.getnames();assert len(names)==len(set(names))
  assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
  assert all(m.isfile() or m.isdir() for m in t.getmembers())
  mn=next(n for n in names if n.endswith('/MANIFEST.json'));prefix=mn[:-len('MANIFEST.json')]
  read=lambda n:t.extractfile(prefix+n).read()
  manifest=json.loads(read('MANIFEST.json'));assert len(manifest['files'])==count
  for n,info in manifest['files'].items():
   payload=read(n);assert len(payload)==info['bytes'] and hashlib.sha256(payload).hexdigest()==info['sha256'],n
  if count==17:
   assert manifest['depends_on']['base_sha256']==hashlib.sha256((root/folder/'attribution-checkpoint-v1.tar.gz').read_bytes()).hexdigest()
   report=json.loads(read('PHASE-ATTRIBUTION.json'));base=json.loads((root/folder/'attribution.json').read_text())
   old={v['shot']:v for v in base['cases']};cases=report['cases'];assert len(cases)==55 and len({v['shot'] for v in cases})==55
   lines=read('phase-attribution.log').decode().splitlines()
   batches=[s for s in lines if s.startswith('ATTR_BATCH ')];shots=[s for s in lines if s.startswith('PAY_SHOT ')]
   assert len(batches)==413 and len(shots)==431
   assert all('full64q_b_phase_T_equal=true' in s and 'original_census_flags_reproduced=true' in s for s in batches)
   assert all('final_bad=true' in s and 'observer_equal=true' in s for s in shots)
   assert len([s for s in lines if s.startswith('PARKED_RAILS ')])==862
   assert read('phase-attribution-stream-before.sha256')==read('phase-attribution-stream-after.sha256')
   for case in cases:
    source=old[case['shot']];assert not source['model_predicted_wrong_value']
    assert case['first_bad_global_stage']==source['first_incorrect_global_stage']['stage']
    for fold in case['matched_fold_losses']:
     event=case['first_PAY_in_that_phase'];assert not event['skip'] and fold['recomputed_low_formula_matches']
     assert (event['phase'],event['tick'],event['rev'])==(fold['phase'],fold['tick'],fold['rev'])
     assert int(event['diff'],16)==-fold['candidate_correction_to_full_payload']%(2**256-2**32-977)
   assert Counter(v['category'] for v in cases)==report['by_observed_mechanism']
   assert report['remaining_unresolved_shots']==[38243,54278,76763,131050]
   assert report['no_new_sampling'] and report['no_candidate_change']
  else:
   report=json.loads(read('SOURCE-COST-RESULT.json'));assert report['at_original_Q']['cap']==1234
   assert report['scoped_extra8']['peak_and_physical_Q']==1242 and report['scoped_extra8']['raw_delta_expected_T']==0
   assert read('all-retained-generation.exit').strip()==b'101' and read('all-retained-cap8-generation.exit').strip()==b'101'
   assert b'y42_bound' in read('all-retained-cap8-generation.log')
   assert not any(n.endswith('/ops.bin') for n in names)
   assert report['no_fresh_sampling'] and report['no_global_arithmetic_correctness_claim']
 results.append(dict(archive=filename,sha256=expected,verified_members=count,independent_crosschecks_pass=True,not_a_scored_result=True))
out=root/'autorun-20261015-2239'/'ROOT_PHASE_RETENTION_REVIEW.json'
out.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
