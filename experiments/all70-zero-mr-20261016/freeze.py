from pathlib import Path
import hashlib,json,tarfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert(R/'run-v2.exit').read_text().strip()=='0';assert(R/'failed-v1/run.exit').read_text().strip()=='1'
d=json.loads((R/'DECLARATION.json').read_text());binding=json.loads((R/'IR-BINDING.json').read_text())
assert binding['source_stream_sha256']==d['source_sha256'] and sha(R.parent/d['source_path'])==d['source_sha256']
assert sha(R/'all70.compact16.bin')==binding['program_sha256'] and sha(R/'all70.compact16.bin.tsv')==binding['program_metadata_sha256']
assert json.loads((R/'SOURCE-PINS-BEFORE.json').read_text())==json.loads((R/'SOURCE-PINS-AFTER.json').read_text())
for name,h in d['compiler_source_lineage'].items():assert sha(R/name)==h,name
refs={binding['program_path']:binding['program_sha256'],str(R.parent/d['source_path']):d['source_sha256']}
refs.update(json.loads((R/'BINARY-PINS.json').read_text()))
summary={'status':'FRESH_ALL70_ZERO_MR_IR_SOURCE_AND_CONTROLS_PASS','authority':False,
 'source_sha256':d['source_sha256'],'program_sha256':binding['program_sha256'],'program_ops':binding['program_bytes']//16,
 'reviewed_generic_compiler_and_kernel_unchanged':True,'generic512_actual_inputs_all_q_b':True,'generic512_scope_assignments_and_live_gate_negative':True,
 'additional_declared_ABI_states':4,'additional_audit_inputs':32,'partial_counts':[0,1,7,11,31,32,63,64,65,511,512],'negative_kernel_controls':4,
 'all512_scored_outputs_checked':True,'original2a_IR_not_loaded_or_transferred':True,
 'required_mask_source_sidecar_sha256':d['required_mask_source_sidecar_sha256'],
 'failed_first_attempt':'The added separate verifier had an ambiguous read trait call. Complete failed source/logs/pins are preserved; corrected only to XofReader::read. The generic compiler, C kernel and declaration are unchanged. Retry used the remaining original900-second wall budget.',
 'phase_or_pass_authority':False,'no_runtime_search_or_production_changes':True}
(R/'TERMINAL-RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n');(R/'SERVER-HASHREFS.json').write_text(json.dumps(refs,indent=2)+'\n')
files=[p for p in R.rglob('*')if p.is_file()and'target'not in p.parts and p.name not in('all70.compact16.bin','evidence.tar.gz','MANIFEST.json','ARCHIVE-RECEIPT.json')]
manifest={str(p.relative_to(R)):sha(p)for p in files};(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(R/'evidence.tar.gz','w:gz')as t:
 for p in sorted(files+[R/'MANIFEST.json']):t.add(p,arcname=str(p.relative_to(R)))
with tarfile.open(R/'evidence.tar.gz')as t:
 for name,h in manifest.items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==h,name
receipt={'status':'VERIFIED','archive_sha256':sha(R/'evidence.tar.gz'),'verified_members':len(manifest),'server_hashrefs':refs,'IR_binding_sha256':sha(R/'IR-BINDING.json'),'terminal_receipt_sha256':sha(R/'TERMINAL-RECEIPT.json')}
(R/'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
