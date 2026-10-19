"""Preserve the failed framing check; audit exact operations and continue."""
import hashlib,json,os,shutil,subprocess,time,socket
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;t=r/'observer'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def raw_digest(path):
 with path.open('rb', buffering=0)as f:
  header=f.read(16);assert header[:8]==b'QECCOPSZ'
  expected=56*int.from_bytes(header[8:],'little')
  proc=subprocess.Popen(['zstd','-dc','--long=27'],stdin=f,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  h=hashlib.sha256();size=0
  for block in iter(lambda:proc.stdout.read(1<<20),b''):h.update(block);size+=len(block)
  error=proc.stderr.read();assert proc.wait()==0,error
  assert size==expected,(size,expected)
  return {'header_hex':header.hex(),'raw_bytes':size,'raw_sha256':h.hexdigest()}

def main():
 assert socket.gethostname()=='LHC-104-070'
 assert (r/'run.exit').read_text().strip()=='1' and not(r/'CONTINUATION-RESULT.json').exists()
 failed=r/'failed-framing-reader-v2';failed.mkdir(exist_ok=False)
 for name in ['continue-v2.py','continuation.log','continuation.exit','SOURCE_FREEZE.json']:
  shutil.copyfile(r/name,failed/name)
 freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
 assert all(sha(t/name)==h for name,h in{**freeze['source_files'],**freeze['protected_files']}.items())
 expected=r.parent/'breakthrough-profile-20261020/observer/prepass.ops.bin'
 assert sha(t/'prepass.ops.bin')==sha(expected)
 native=raw_digest(r/'cap-1234.ops.bin');reference=raw_digest(expected)
 assert native==reference,'Serialized operations differ; no continuation permitted'
 (r/'CAP1234-ENCODING-CONTROL.json').write_text(json.dumps({'status':'EXACT_HEADER_AND_ALL_OPERATION_BYTES_IDENTICAL',
  'reason_original_admission_failed':'Diagnostic writer requests zstd window_log27; protected writer uses its default. Compressed framing differs, operations do not.',
  'native_compressed_sha256':sha(r/'cap-1234.ops.bin'),'prepass_compressed_sha256':sha(expected),'raw':native,
  'no_regeneration_of_control_and_no_source_change':True},indent=2)+'\n')
 results=[]
 for cap in freeze['caps']:
  env=os.environ.copy();env['BREAK_CAP']=str(cap)
  start=time.time();dest=r/f'cap-{cap}.ops.bin'
  if cap==1234:rc=0
  else:
   with(r/f'cap-{cap}.out').open('xb')as output,(r/f'cap-{cap}.log').open('xb')as log:
    run=subprocess.run(['/usr/bin/time','-v',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=output,stderr=log)
   rc=run.returncode
   if rc==0:(t/'ops.bin').rename(dest)
  result={'cap':cap,'exit':rc,'seconds':time.time()-start,'status':'GENERATION_FAILED'if rc else'RAW_ARITHMETIC_GENERATION_ONLY'}
  if rc==0:
   with dest.open('rb')as f:header=f.read(16)
   result.update(stream_sha256=sha(dest),ops=int.from_bytes(header[8:],'little'))
   phases=[]
   for line in(r/f'cap-{cap}.log').read_text().splitlines():
    if line.startswith('BREAK_PHASE\t'):
     name,end,active,peak,ccx,ccz=line.split('\t')[1:]
     phases.append({'phase':name,'end':int(end),'peak':int(peak),'active_end':int(active),'emitted_ccx':int(ccx),'emitted_ccz':int(ccz)})
   assert phases[-1]['end']==result['ops']
   result['phases']=phases;result['builder_max_active']=max(p['peak']for p in phases)
   (r/f'cap-{cap}-phase.tsv').write_text(''.join(f"{p['phase']}\t{p['end']}\t{p['end']}\t0\n"for p in phases))
   if cap==1234:result['full_raw_operation_identity_control']=True
  (r/f'cap-{cap}-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
  results.append(result)
  (r/'CONTINUATION-PROGRESS.json').write_text(json.dumps({'status':'DIAGNOSTIC_ADMISSION_ONLY','results':results},indent=2)+'\n')
  print(json.dumps({k:v for k,v in result.items()if k!='phases'}),flush=True)
 assert all(sha(t/name)==h for name,h in{**freeze['source_files'],**freeze['protected_files']}.items())
 (r/'CONTINUATION-RESULT.json').write_text(json.dumps({'status':'RAW_CAP_ADMISSION_STUDY_COMPLETE_NO_SCORED_RESULT','results':results},indent=2)+'\n')

if __name__=='__main__':
 try:main()
 except BaseException:
  (r/'continuation-v3.exit').write_text('1\n');raise
 else:(r/'continuation-v3.exit').write_text('0\n')
