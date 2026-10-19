"""Seal finished local research, including all failed admissions and binary hashes."""
import hashlib,io,json,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;name=sys.argv[1]
assert name in ['product-classical-closure-20261019','product-classical-cap11-20261019','product-anf256-20261019','product-anf-witness-20261019'];r=ws/name
assert (r/'run.exit').read_text().strip()=='0'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
if name=='product-classical-closure-20261019':
    result=json.loads((r/'closure9.json').read_text());assert result['input_full_sha3_256']==result['output_full_sha3_256']
    note='Existing tested cap9 pass on frozen classical12 is byte-identical: no further reduction on a second application. No prototype, nonce, gate or record.44.41s single local core, peak RSS1974764KiB.'
elif name=='product-classical-cap11-20261019':
    result=json.loads((r/'RESULT.json').read_text());assert result['compat9_complete_raw_hash_equal']
    if result['source']['input_full_sha3_256']==result['source']['output_full_sha3_256']:
        note='All7 primitive/exhaustive2048-row tests pass. Cap9 complete hash control passes. Cap11 output is unchanged, so no useful prototype, nonce, gate or record.'
    else:
        assert result['control']['status']=='PROTECTED_SIMULATOR_CLASSICAL_FACTOR_FULL_TRANSCRIPT_CONTROL_PASS'
        saved=result['control']['saved_executed_Toffolis_total_on_512_control_shots']
        note=f'All7 primitive/exhaustive2048-row tests and cap9 complete-hash control pass. Cap11 source changes;512 full quantum/classical/phase/physical-RNG controls pass, total executed T saved={saved}. This is finite component/source evidence, not a statistical gate or scored record. No native candidate or nonce. Two pre-compiler admissions are preserved with complete original source hashes.'
else:
    result=json.loads((r/'RESULT.json').read_text());src=result['source'];same=src['input_sha3_256']==src['output_sha3_256']
    if name=='product-anf256-20261019':
        note='All9 primitive/polynomial controls pass. Fixed256-term/degree12 full source screen finishes with0 sites and identical complete17,889,635-op raw hash.460.56s elapsed, peak RSS2159772KiB.2,510,716 abstraction cuts are safe fresh whole-result fallbacks, not assumed zeros. No native candidate, gate, nonce or score.'
        assert same and src['sites_count']==0
    else:
        assert result['disabled_complete_report_and_stream_identical']
        note=f'All16 controls and complete disabled-mode report/stream control pass. Enabled current-wire product witness sites={result["current_wire_witness_sites"]}. '
        if same:note+='Full raw output is unchanged: no prototype or executed saving.'
        else:
            assert result['control']['status']=='PROTECTED_SIMULATOR_CLASSICAL_FACTOR_FULL_TRANSCRIPT_CONTROL_PASS'
            note+=f'All512 raw complete q/c/phase/physical-RNG controls pass, total executed T saved={result["control"]["saved_executed_Toffolis_total_on_512_control_shots"]}.'
        note+=' Component/source evidence only; no native candidate, gate, nonce or score.'
with (r/'STATUS.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\n## Completed local experiment\n\n'+note+'\n')
files={};omitted={}
for p in r.rglob('*'):
    rel=p.relative_to(r)
    if not p.is_file() or any(s in rel.parts for s in ['__pycache__','target','evidence']):continue
    if p.name.startswith(('evidence','EVIDENCE','LOCAL-VERIFICATION')):continue
    item={'bytes':p.stat().st_size,'sha256':sha(p)}
    (omitted if p.suffix=='.bin' or p.stat().st_size>5_000_000 else files)[rel.as_posix()]=item
manifest={'at_utc':datetime.now(timezone.utc).isoformat(),'environment':'existing local WSL Ubuntu, one core','scope':note,'included_files':files,'binary_inputs_outputs_and_executables_retained_locally':omitted}
p=r/'evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for key in sorted(files):a.add(r/key,arcname=key)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files),'scope':note},indent=2)+'\n')
with tarfile.open(p) as a:
    for key,item in files.items():
        raw=a.extractfile(key).read();assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
(r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'FINISHED_ARCHIVE_AND_ALL_MEMBERS_VERIFIED','files':len(files),'sha256':sha(p)},indent=2)+'\n')
print(name,note)
