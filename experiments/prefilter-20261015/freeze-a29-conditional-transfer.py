from pathlib import Path
import hashlib, json

r = Path(__file__).resolve().parent
out = r / 'a29-conditional-certificate-v1'
assert not out.exists(), 'Immutable receipt already exists'
out.mkdir()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''): h.update(b)
    return h.hexdigest()
def pin(p, expected=None):
    p = p.resolve(); s = sha(p)
    if expected: assert s == expected, (p, s, expected)
    return {'path': p.relative_to(r.parent).as_posix(), 'sha256': s, 'bytes': p.stat().st_size}
def write(name, x):
    (out/name).write_bytes((json.dumps(x, indent=2)+'\n').encode())

old = '2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
a29 = '1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522'
candidate = '0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b'
g = '355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3'
mask = '560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d'
cov = r/'a29-conditional-coverage-v1'; sub = r/'a29-conditional-subset-v1'
for folder in [cov, sub]:
    assert (folder/'run.exit').read_text().strip() == '0'
    assert (folder/'before.sha256').read_bytes() == (folder/'after.sha256').read_bytes()
c = json.loads((cov/'summary.json').read_text()); s = json.loads((sub/'result.json').read_text())
assert len(c['points']) == len(s['rows']) == 445
assert (s['old431_original_certified'],s['old431_retained'],s['old431_lost_to_guard']) == (421,418,3)
rows = []
for i, (p, q) in enumerate(zip(c['points'], s['rows'])):
    assert q['index'] == i
    assert p['discrepancy_guard'] == (not q['conditional_transfer_guard_false'])
    assert q['retained_certificate'] == (q['old_mask_certified_wrong'] and not p['discrepancy_guard'])
    rows.append({'index':i,'group':p['group'],'batch':p['batch'],'lane':p['lane'],
                 'input_fixture_line':i,'G':p['discrepancy_guard'], **{k:v for k,v in q.items() if k!='index'}})
write('EXACT_RETAINED_SUBSET.json', {'status':'FIXED_EXISTING_WITNESS_SUBSET_NO_NEW_CENSUS',
    'fixture':pin(cov/'fixed445-inputs.tsv','f958e8665b8d9c7af59e848bddd4864e9fe951db3a835832933d6418cae4a922'),
    'old431_original_certified':421,'old431_retained':418,'old431_excluded':3,
    'repair14_original_certified':14,'repair14_excluded':14,'rows':rows})

proof_paths = [
 'evidence/mask-freeze-v3.json','evidence/mr-mask-tip-v3.json','MR-MASK-ABI.txt',
 'a29-conditional-family-v1/PREDECLARED-FAMILY.json',
 'a29-conditional-family-v1/actual-fullstream-frame-binding.json',
 'a29-conditional-family-v1/family-summary.json',
 'a29-conditional-family-v1/live-classical-proof.json',
 'a29-conditional-validation-v1/summary.json',
 'a29-conditional-prefix-v1/global.json','a29-conditional-prefix-v1/local-guards.json',
 'a29-conditional-prefix-v1/INDUCTION.md',
 'a29-conditional-prefix-v1/ROOT_INDEPENDENT_REVIEW.json',
 'a29-conditional-coverage-v1/summary.json','a29-conditional-subset-v1/result.json',
 'a29-conditional-certificate-v1/EXACT_RETAINED_SUBSET.json',
 'evidence/a29-paired-family-archive-receipt.json',
 'evidence/a29-conditional-prefix-archive-receipt.json']
pins = [pin(r/p) for p in proof_paths]
cache = r.parent/'product-exact-20261015/repair67-universal-20261016'
cache_cert = pin(cache/'CACHE_EQUIVALENCE_CERTIFICATE.json','3cb037399462d45683c9790793ed1bfbff2df2934898f38f9ffe2cd857ff4d39')
cache_transfer = pin(cache/'PER_INPUT_MASK_TRANSFER.json','0bfcc1dd3657e1c8eb6ae8ce404c1c91da22eb9c7b3622d3ad8dbfecbf12a1e3')
abi = pin(r.parent/'product-exact-20261015/REPAIR67_ABI.json','61cb74a939cd5370e1701bb8850e2c6d642e6776893e14038f2d89f848f84d1c')
cert = {
 'status':'SOURCE_BOUND_CONDITIONAL_VALUE_MASK_TRANSFER_THEOREM_NO_RUNTIME_AUTHORITY',
 'original_stream_sha256':old,'original_mask_sha256':mask,'A29_stream_sha256':a29,
 'public_discrepancy_guard':pin(r/'a29-conditional-prefix-v1/public-discrepancy-guard.bin',g),
 'theorem': 'For each declared input x and scored bit j, if raw G(x)=0 and raw original dependency D_j(x)=0, every A29 measurement tape produces the same scored bit as original4b at zero MR. The audited A29-relative67 cache projection preserves that value for every candidate measurement tape. Thus a mismatch of that original zero-MR bit against the protected curve result is a sufficient rejection certificate.',
 'combined_dependency':'D_new,j(x) = D_original,j(x) OR G(x)',
 'known_bit':'NOT D_new,j(x); equivalently (NOT D_original,j(x)) AND (NOT G(x))',
 'polarity': 'MRMASK01 raw root is dependency/discrepancy; MaskProgram.eval complements it. G=1 requires fallback, never rejection on this certificate.',
 'proof_chain': [
   'Each of29 actual old/new helper pairs is universally proved in one common immutable input namespace with arbitrary dirty entry q/classical bits and independent changed-middle MR. All physical q-output differences, not only the next payload bit, are retained.',
   'Every old/new frame digest and all outside-operation byte equality are bound to the actual final streams. All29 local q contracts have no entry-zero assumptions.',
   'Exact classical ANF proves equal live versions under identical prefix/suffix MR roles. Unequal versions are killed by an unchanged depth-zero unconditional overwrite before any read or captured guard. Replacement boundary scope stacks are empty.',
   'Actual A29 finite prefix proves every substituted local q port input-only, not a zero-MR coincidence; retained coefficient definitions make the composed public1024-port G exact.',
   'Induction on earlier false local guards transfers common entries and live interfaces from A29 to original; outside equal operations preserve them. This proves final q equality under the MR projection when G=0.',
   'Original2a-bound per-bit dependency proof and universal A29-relative67 cache equivalence compose only through this new conditional theorem, never by assuming an unchanged arithmetic function.'
 ],
 'proof_receipts':pins,
 'ABI':{'public_ports':1024,'order':['P.x','P.y','A.x','A.y'],'bits_within_coordinate':'LSB first',
        'scored_outputs':512,'order_scored':['reg0 x','reg1 y'],'registers':'Four ordered256-bit declarations; quantum regs0/1 and classical regs2/3.',
        'candidate67_ABI_receipt':abi,'candidate_qubits':1234,'candidate_classical_bits':66245,
        'fallback_classical_index_min_width':32,'fallback_workspace_min_classical_words':66245,
        'reject_u16_truncation':True},
 'A29_relative_cache67':{'candidate_stream_sha256':candidate,'universal_certificate':cache_cert,
   'conditional_transfer':cache_transfer,'prefix_sha256':'c59cde58aa9ce2cf9b8f99ff4246a0848a1d84ef0648ba2818b3895ed8503c35',
   'pre_tail_ops':17898304,'nonce_rule':'Only the audited identical prefix plus48 adjacent XX identity pairs onq0/q1; verify any new tail.',
   'own_Fiat_inputs_required':True},
 'fixed_existing_coverage':{'inputs':445,'old_value_witnesses':431,'old_certified':421,'retained':418,
   'parent_only_repair_lanes':14,'parent_only_original_certified':14,'parent_only_G_true':14,
   'new_eligibility_sample':False,'new_source_tuning':False},
 'cost_scope':{'guard_component_median_seconds_445':c['guard_only_timings']['median_seconds'],
   'conditions':c['guard_only_timings']['conditions'],'end_to_end_runtime_claim':False,
   'recommended_order':'Evaluate G only after original-mask and original zero-MR value propose a rejection.'},
 'runtime_integration_requirements':[
   'Independently bind and review the composite binary, source variants, input/output mapping, guard evaluator and all library hashes.',
   'Use candidate final-source own Fiat inputs; preserve all MR ordinals/draws and arbitrary enclosing snapshots in full candidate fallback.',
   'Assert u32 or wider classical IDs and workspace>=66245 before loading candidate67; unknown or unavailable certificate results must fall back.',
   'Validate protected known-bit containment, exact fallback/full phase/garbage and scheduler bookkeeping on distinct controls, then perform a measured cost gate.',
   'Official unchanged benchmark, frozen fresh failure census eligibility, nonce disclosure and lowest-pass policy remain separate.'
 ],
 'not_claimed':['All scored bits MR-independent','G=1 implies a final difference','Phase/garbage correctness transfers','Physical MR tapes or Fiat transcripts transfer','A passing nonce','A scored record','Operational/search authority']
}
write('CONDITIONAL_TRANSFER_CERTIFICATE.json',cert)
print(json.dumps({'certificate_sha256':sha(out/'CONDITIONAL_TRANSFER_CERTIFICATE.json'),
                  'subset_sha256':sha(out/'EXACT_RETAINED_SUBSET.json'),'folder':str(out)}))
