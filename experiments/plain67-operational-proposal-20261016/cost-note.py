from pathlib import Path
import hashlib,json,math

R=Path(__file__).resolve().parent
pilot=R.parent/'plain67-persistent-pilot-20261016'
receipt=json.loads((pilot/'ARCHIVE-RECEIPT.json').read_text())
assert receipt['archive_sha256']=='28495fad94ee52e130df1acc0023fc62f2df979c2167b3e6430aa06e684d3eb2'
assert hashlib.sha256((pilot/'evidence.tar.gz').read_bytes()).hexdigest()==receipt['archive_sha256']
result=json.loads((pilot/'RESULT.json').read_text())
trials=[]
for item in result['trials']:
 if not item['name'].startswith('trial'):continue
 mean4=item['observed_four_core_mean_model_hours']
 mean8=mean4/2
 trials.append({'mode':item['mode'],'measured_four_core_group_seconds':item['group_elapsed_seconds_including_startup'],
  'measured_four_core_amortized_rate':item['observed_four_core_amortized_nonces_per_second'],
  'ideal_linear64_mean_hours_NOT_MEASURED':mean4/16,
  'ideal_linear8_mean_hours_NOT_MEASURED':mean8,
  'ideal_linear8_probability_of_at_least_one_pass_within24hours_model_only':-math.expm1(-24/mean8)})
note={'status':'DISABLED_COST_PROPOSAL_SUPPLEMENT_NO_OPERATIONAL_AUTHORITY',
 'pilot_archive_sha256':receipt['archive_sha256'],'terminal_receipt_sha256':receipt['terminal_receipt_sha256'],
 'own_candidate_failed_batches':4162,'own_census_batches':32768,'packet_batches':141,
 'expected_nonces_model':result['expected_nonces_model'],'trials':trials,
 'interpretation':'The user affordability criterion of about one day on64 threads is cleared only as an ideal-linear model. A proposed8-thread24-hour hedge has an ideal-model success probability near17%, not a24-hour expected completion. Resource scaling, cache contention and future co-tenancy are unmeasured.',
 'eligibility':'The old gate was paired against original4b. A new public product record with a lower disclosed failure rate requires a new then-current eligibility comparison; cost cannot override that gate.',
 'co_tenancy':'Original25 production had terminated before these timing trials. No causal comparison against earlier repaired67 timings or generic/direct speedup is claimed.',
 'search_started':False,'new_source_or_executable_created':False}
(R/'COST-NOTE.json').write_text(json.dumps(note,indent=2)+'\n')
print(json.dumps(note))
