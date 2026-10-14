"""Freeze completed second-checkpoint component evidence and failures."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).parent
AREA=HERE.parents[2]/'research-output/overnight-20261014/toffoli'
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,d):HERE.joinpath(name).write_bytes((json.dumps(d,indent=2)+'\n').encode())

def main():
    raw=AREA/'toffoli-exact-planes-20261014.json';d=json.loads(raw.read_text())
    save('exact-planes-summary.json',{
        **{k:d[k] for k in ['status','source_lf_sha256','netlist_sha256','exact_domain_size','seconds','all_63_planes_completed','limits']},
        'raw_receipt_sha256':hashfile(raw),'raw_receipt_bytes':raw.stat().st_size,
        'status_counts':dict(Counter(r['status'] for r in d['planes'])),
        'planes':[{'hyperplane':r['hyperplane'],'status':r['status'],'final_ANDs':r['final_ANDs']} for r in d['planes']],
        'interpretation':'No <=30-AND complete-value program lies within the original 46-function span under these trusted affine-factor solver results. Four planes use exact GF quadratic obstructions; 59 use Z3 UNSAT without formal proof certificates. Programs introducing functions outside that span remain open.'})
    raw=AREA/'toffoli-consume-two-exact-20261014.json';d=json.loads(raw.read_text())
    d.update(raw_receipt_sha256=hashfile(raw),value_rank_bound=24,value_rank_bound_unattainable=True,
             interpretation='The selected constructor-plus-two-consumer contract has raw rank17 and desired rank41. Four legal ANDs followed by trusted affine-factor UNSAT prohibit the rank24 circuit. This is not a complete Toffoli cost bound; changed phase ownership and cleanup remain unverified. No formal solver proof certificate.')
    save('consume-two-exact-summary.json',d)
    HERE.joinpath('bank-phase-basis.json').write_bytes(AREA.joinpath('phase-basis-reverse.json').read_bytes())
    HERE.joinpath('bank-phase-schedule.json').write_bytes(AREA.joinpath('phase-schedule.json').read_bytes())
    rows=[]
    native=AREA/'toffoli-bank-loan-native-20261014.log'
    for line in native.read_text().splitlines():
        if line.startswith('TOFFOLI_BANK_COMPONENT'):
            r={k:int(v) for k,v in re.findall(r'(\w+)=([0-9]+)',line)}
            r['mean_delta']=(r['new_executed']-r['old_executed'])/r['shots'];rows.append(r)
    body={}
    for line in AREA.joinpath('toffoli-bank-receipts-v4-20261014.log').read_text().splitlines():
        if line.startswith('TOFFOLI_BODY_LEDGER'):
            d=dict(re.findall(r'(\w+)=([^ ]+)',line));body[int(d['room']),int(d['tick']),d['bank']]=d
    pairs=[]
    for room,tick,on in body:
        if on=='true':
            old=body[room,tick,'false'];new=body[room,tick,'true']
            pairs.append({'room':room,'tick':tick,'old_diagnostic_mean':float(old['diagnostic_mean']),
                          'new_diagnostic_mean':float(new['diagnostic_mean']),
                          'delta':float(new['diagnostic_mean'])-float(old['diagnostic_mean']),
                          'old_peak':int(old['peak']),'new_peak':int(new['peak'])})
    def hashes(v):
        return {line.split('/')[-1]:line.split()[0] for line in AREA.joinpath(f'toffoli-bank-receipts-{v}-20261014-stream-hashes.txt').read_text().splitlines()}
    streams=hashes('v2');assert streams==hashes('v4') and len(streams)==136
    save('bank-component-streams.json',{'algorithm':'SHA256 of canonical QECCOPSZ files written by unchanged build_circuit serializer',
        'server_directory':'/home/hclau/ecdsa_research/overnight-20261014/toffoli/toffoli-bank-receipts-v2-20261014-streams',
        'diagnostic_report_enabled_streams_identical':True,'stream_count':len(streams),'streams':streams})
    save('bank-component-receipt.json',{'status':'native_values_and_tested_phases_passed_complete_component_gate_cost_worse',
        'source_recipe':'31 initial ANDs; six early measurement phase erasures; 25 bank directions through ladder; six unconditional AND regenerations; original cleanup',
        'native_cases':53542912,'native_phase_coefficients':85,'native_upper_words':38,
        'native_tests':3,'native_exit':0,'native_log_sha256':hashfile(native),'native_settings_sha256':hashfile(AREA/'toffoli-bank-loan-native-20261014.settings'),
        'native_wall_seconds':84.08,'native_peak_rss_KiB':1158564,
        'paired_fold_rooms':rows,'payload_body_pairs':pairs,'payload_pair_count':len(pairs),
        'limits':'Fold checks cover all16384 raw low-input states with38 upper words, zero and85 measurement coefficients. Paired room tests use3 upper words and independent measurement words. Full body pairs are builder-only resource diagnostics, not native correctness tests. No full point-addition benchmark or qualified resource record.',
        'failures_preserved':[
            {'job':'toffoli-bank-receipts-20261014','status':'failed_compilation_mutability_fixture_only','exit':101,'log_sha256':hashfile(AREA/'toffoli-bank-receipts-20261014.log'),'pid':'not captured before short compiler failure'},
            {'job':'toffoli-bank-receipts-v2-20261014','status':'streams_saved_but_diagnostic_counter_disabled','exit':0,'pid':2391217,'log_sha256':hashfile(AREA/'toffoli-bank-receipts-v2-20261014.log')},
            {'job':'toffoli-bank-receipts-v3-20261014','status':'streams_saved_but_research_report_switch_inactive','exit':0,'log_sha256':hashfile(AREA/'toffoli-bank-receipts-v3-20261014.log')},
            {'job':'toffoli-bank-receipts-v4-20261014','status':'complete_diagnostic_ledger_and_identical_streams','exit':0,'log_sha256':hashfile(AREA/'toffoli-bank-receipts-v4-20261014.log')}],
        'production_width_tradeoff':'Separate complete builder failed at inherited allocator before-state assertion on forward tick87. Complete peak not available; product tradeoff remains unmeasured.'})
    build=json.loads(AREA.joinpath('receipt.json').read_text())
    save('bank-product-failed-builder.json',{'status':'failed_allocator_interface_before_complete_stream','pid':2402626,'exit':101,
        'failure':'y42 allocator before forward tick87 differs from the recorded baseline state',
        'expected_allocator_hash':14727610921648462284,'observed_allocator_hash':3735620290340593712,
        'log_sha256':hashfile(AREA/'run.log'),'settings_sha256':hashfile(AREA/'settings.txt'),
        'terminal_receipt':build,'scope':'Failure is integration evidence. No complete peak, diagnostic gate mean, scored stream or record. Inherited allocator assertion preserved; no arbitrary rebinding.'})
    paths=['exact-planes-summary.json','consume-two-exact-summary.json','bank-phase-basis.json','bank-phase-schedule.json','late-phase-rotations.json','cubic-cleanup.json','bank-component-streams.json','bank-component-receipt.json','bank-product-failed-builder.json','bank-loan-native.patch','bank-product.patch','bank-product-prelaunch.json']
    save('second-checkpoint-receipt.json',{'collected_at_utc':datetime.now(timezone.utc).isoformat(),
        'status':'all listed jobs terminal; native component positive correctness/cost negative; production builder failed; no record',
        'baseline_revision':'c5bb1ec876db859a3f9f8a9052c140a145df834e',
        'protected_changes':[],'qualified_score':None,'files':{name:hashfile(HERE/name) for name in paths},
        'server_roots':['/home/hclau/ecdsa_research/overnight-20261014/toffoli','/home/hclau/ecdsa_research/overnight-20261014/toffoli-bank-product-evidence/builder'],
        'next':'Restore baseline allocator boundary ordering by a reviewed exact mechanism before completing the product width measurement; pursue alternate phase cleanup contracts.'})
    print('second checkpoint frozen',len(paths),'files')

if __name__=='__main__':main()
