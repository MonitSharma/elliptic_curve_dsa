"""Fixed67 freshly generated and universally audited on uniform ALL70 source."""
from pathlib import Path
import copy,hashlib,json,os,shutil,subprocess,time
r=Path(__file__).resolve().parent;d=r/'all70-cache67-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (d/'base-launcher.exit').read_text().strip()=='0'
receipt=json.loads((d/'BASE_NATIVE_RECEIPT.json').read_text());source=r/'candidate-all70-base/ops.bin';assert sha(source)==receipt['source_sha256']
plan=json.loads((d/'DECLARATION.json').read_text());assert len(plan['stages'])==67
exe=r/'target-flags/release/product_paired_diagnostic';verifier=r/'target-cache-certificate-v2/release/product_paired_diagnostic'
assert sha(verifier)=='2e9f5ee6ed4ea1fa5b625f38298a71e05ce885778db7aed1064b23d2ee657091'
trusted=r/'cache-certificate-v2-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json';assert sha(trusted)=='4857f8255c6aa85f0c6cb84720c6d5690aaca060f2758a8c517bd43fc5e2f04e'
old=json.loads(trusted.read_text());sources={str(p.relative_to(r/'cache-certificate-v2-tool')):sha(p) for p in (r/'cache-certificate-v2-tool').rglob('*') if p.is_file() and 'target' not in p.relative_to(r/'cache-certificate-v2-tool').parts};assert sources==old['source_files_sha256']
bindings={'source_sha256':sha(source),'declaration_sha256':sha(d/'DECLARATION.json'),'generator_sha256':sha(exe),'verifier_sha256':sha(verifier),'verifier_source_files_sha256':sources,'trusted_kernel_provenance_certificate_sha256':sha(trusted),'scope':'Fresh ALL67 cache equivalence relative to changed ALL70 arithmetic, all ABI inputs and all original MR assignments. No equivalence to original arithmetic and no old value mask transferred.'}
assert json.loads((d/'CACHE_BINDINGS.json').read_text())==bindings
frozen=d/'all70-parent.bin';assert sha(frozen)==receipt['source_sha256'];previous=frozen
attempt=d/'launcher-cwd-repair-attempt1';assert json.loads((attempt/'RECEIPT.json').read_text())['source_recipe_changed']is False
records=json.loads((attempt/'LAST_COMPLETE_STAGE_RECEIPTS.json').read_text());assert 0<len(records)<25;start=len(records)
for i,row in enumerate(records,1):
 assert row['stage']==i and row['config']==plan['stages'][i-1] and row['status']=='UNIVERSAL_PASS' and row['input_sha256']==sha(previous)
 for name,digest in [('input_stream','input_sha256'),('output_stream','output_sha256'),('audit_log','audit_log_sha256')]:assert sha(r/row[name])==row[digest]
 if row['lease_log']!='=':assert sha(r/row['lease_log'])==row['lease_log_sha256'] and 'UNIVERSAL_CACHE_CERTIFICATE_PASS'in(r/row['audit_log']).read_text()
 previous=r/row['output_stream'];print(json.dumps(row),flush=True)
manifest=d/'chain.manifest';manifest.write_text(''.join(str(r/row['output_stream'])+' '+('='if row['lease_log']=='='else str(r/row['lease_log']))+'\n'for row in records))
(d/'CACHE_STAGE_RECEIPTS.json').write_text(json.dumps(records,indent=2)+'\n')
(d/'CWD_REPAIR_RESUME.json').write_text(json.dumps({'resumed_from_complete_stage':start,'previous_driver_sha256':sha(attempt/'run_all70_cache67.py'),'resume_driver_sha256':sha(Path(__file__)),'completed_streams_unchanged':True,'recipe_declaration_sha256':sha(d/'DECLARATION.json'),'diagnostic_manifest_paths':'absolute','diagnostic_cwd':str(r),'no_numerical_packets_yet':True},indent=2)+'\n')
env=os.environ.copy();env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
for i,spec in enumerate(plan['stages'],1):
 if i<=start:continue
 available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;assert available>=124*1024**3
 name=d/f"all70-{i:02d}-{spec['family']}-{spec['atom_cap']}";output=Path(str(name)+'.bin');log=Path(str(name)+'-generate.log');audit=Path(str(name)+'-universal.log')
 env.update(EXACT_MODE='cache' if spec['family']=='affine' else 'cache-'+spec['family'],CACHE_ATOM_CAP=str(spec['atom_cap']),ANF_PAIR_CAP=str(spec['pair_cap']),CACHE_PRODUCT_CAP=str(spec['product_cap']),CACHE_SPLIT='1',CACHE_RANK=spec['rank'])
 with Path(str(name)+'-preflight.json').open('w') as out:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=out,check=True)
 assert sha(exe)==bindings['generator_sha256'] and sha(verifier)==bindings['verifier_sha256'];before=sha(previous)
 with log.open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(exe),str(previous),str(output)],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
 after=sha(output);assert sha(previous)==before;mapping='=' if after==before else str(log.relative_to(r))
 with manifest.open('a') as out:out.write(str(output)+' '+('='if mapping=='='else str(log))+'\n')
 if mapping=='=':audit.write_text('UNIVERSAL_BYTE_IDENTITY_PASS\n')
 else:
  with audit.open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(verifier),str(previous),str(output),str(log),spec['family']],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
 record={'stage':i,'config':spec,'input_stream':str(previous.relative_to(r)),'input_sha256':before,'output_stream':str(output.relative_to(r)),'output_sha256':after,'lease_log':mapping,'lease_log_sha256':sha(log),'audit_log':str(audit.relative_to(r)),'audit_log_sha256':sha(audit),'status':'UNIVERSAL_PASS'};records.append(record)
 (d/'CACHE_STAGE_RECEIPTS.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(record),flush=True);previous=output
 if i in [25,67]:
  checkpoint=d/f'stage-{i}.manifest';shutil.copy2(manifest,checkpoint)
  for packet in ['independent','structured']:
   with (d/f'stage-{i}-{packet}.log').open('wb') as out:subprocess.run(['/usr/bin/time','-v',str(r/'target-anchored-replay/release/product_paired_diagnostic'),str(frozen),str(previous),'+'+str(checkpoint),packet,str(d/f'stage-{i}-{packet}.tsv')],stdout=out,stderr=subprocess.STDOUT,env=env,cwd=r,check=True)
  for script,namepart in [('stream_resources.py','resources'),('stream_prefix_manifest.py','prefix')]:
   with (d/f'stage-{i}-{namepart}.jsonl').open('w') as out:subprocess.run(['python3',str(r/script),str(previous)],stdout=out,check=True)
freeze={'status':'ALL70_FIXED67_FRESH_GENERATION_UNIVERSAL_AND512_STATE_PHASE_PASS','base_revision':plan['base_revision'],'all70_parent_stream':str(frozen.relative_to(r)),'all70_parent_sha256':sha(frozen),'external_stream':str(previous.relative_to(r)),'external_stream_sha256':sha(previous),'stages':plan['stages'],'chain_manifest':str(manifest.relative_to(r)),'declaration_sha256':sha(d/'DECLARATION.json'),'bindings_sha256':sha(d/'CACHE_BINDINGS.json'),'stage_receipts_sha256':sha(d/'CACHE_STAGE_RECEIPTS.json'),'native_final_port':'pending','fresh_32768_original4b_gate':'pending','score':None}
(r/'ALL70_FIXED67_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps(freeze),flush=True)
