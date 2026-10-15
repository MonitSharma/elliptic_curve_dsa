from pathlib import Path
import json,hashlib,datetime
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016')
x=json.loads((r/'square-interfaces.json').read_text());assert len(x['rows'])==4
assert sorted(row['shift']for row in x['rows'])==[4,6,10,32]
assert(r/'protected-dirty-square.exit').read_text().strip()=='0'
assert(r/'terminal-proof-dirty.exit').read_text().strip()=='0'
proof=json.loads((r/'terminal-proof.json').read_text());assert proof['square']['arbitrary_dirty_donor_four_CCX_variant']
for row in x['rows']:
 assert len(row['whole_window_matches'])==1 and row['terminal_candidates']==1
 assert row['next_framed_by_entire_old_window']and row['old_entire_window_balanced']
 assert row['guard']['scope_depth']==0 and row['guard']['kind']=='exact'and row['guard']['lower']=='1'
 assert len({0,row['previous'],row['penultimate'],row['top_bit'],row['next']})==5
f=dict(status='FROZEN BEFORE CANDIDATE GENERATION AND ANY SAMPLE',
 created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 base_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',
 base_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',
 family='ALL four source wcin_windows calls with high.len()==130; every NAF term shift4/6/10/32',
 admission='unique literal entire old window; next payload U absent from every old quantum read/write/phase; balanced top-level window; exact local dirty-donor primitive and restored donor',
 on_any_failure='REJECT ALL FOUR; never omit or substitute any site',
 implementation='four-CCX borrowed-dirty C3X(p,a,T;U), then unchanged original terminal CCX; donor=q0',
 higher_bits='only bit U at the old window boundary changes; every higher bit is explicitly framed; exact width+1 truncated signed addition when old incoming carry represents its defined arithmetic value',
 dirty_entry='local gate/whole-window relative theorem quantifies arbitrary incoming q/b/guard/MR and dirty donor, without assuming inherited arithmetic correct',
 expected_delta=dict(added_native_CCX=16,added_expected_T=16,added_Q=0,added_B=0,added_MR=0,old_MR_ordinals='identity'),
 sites=[{k:row[k]for k in ['shift','high_width','inv','actual_window','actual_terminal','previous','penultimate','top_bit','next','old_window_sha256']}for row in x['rows']],
 fresh_gate=dict(label='public4b-all-C130-square-dirty-carry-independent-20261016-v1',start=0,batches=32768,lanes=64,inputs_per_source=2097152,
  source_order=['original4b','candidate'],workers_per_source=4,simultaneous_sources=False,
  strict_pass='candidate failed_batches <= original failed_batches AND candidate failed_batches/32768*141 <=18',resample=False,
  require_every_value_phase_dirty_change=True,nonce_search=False,official_packet=False),
 proof_files={name:hashlib.sha256((r/name).read_bytes()).hexdigest()for name in ['prove-terminal.py','terminal-proof.json','protected_terminal.rs','protected-dirty-square.json','square-interfaces.json','square-observer-source.json']})
p=r/'SQUARE4-PREDECLARATION.json';assert not p.exists();p.write_text(json.dumps(f,indent=2)+'\n');print(json.dumps(f))
