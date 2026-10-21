import json,os,subprocess,traceback
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-recycle-final-20261021';n=ws/'breakthrough-recycle-nonce-20261021'
env=dict(os.environ,CARGO_BUILD_JOBS='4',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
try:
 with(n/'controller.log').open('xb')as out:
  p=subprocess.Popen(['python3','-u',str(n/'run.py')],stdout=out,stderr=subprocess.STDOUT,env=env);(n/'controller.pid').write_text(str(p.pid)+'\n');assert p.wait()==0
 sr=json.loads((n/'SEARCH-RESULT.json').read_text())
 if sr['status']=='LOWEST_PASS_FOUND':
  with(r/'finalize.log').open('xb')as out:
   p=subprocess.Popen(['python3','-u',str(r/'finalize.py')],stdout=out,stderr=subprocess.STDOUT,env=env);(r/'finalize.pid').write_text(str(p.pid)+'\n');assert p.wait()==0
  result={'status':'UNCHANGED_BENCHMARK_COMPLETE_AWAIT_LOCAL_EVIDENCE_REVIEW','nonce':sr['selected_nonce'],'scope':'No upload by this controller. Verify complete source/evidence, refresh current records and require strict actual Toffoli improvement before authorized official submission.'}
 else:result={'status':'DECLARED_NONCE_PREFIX_EXHAUSTED_PRESERVE_NO_BENCHMARK','scope':'No passing nonce, no benchmark/upload. Preserve frozen source, gate and every rejection.'}
 (r/'PIPELINE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'pipeline.exit').write_text('0\n')
except BaseException:
 (r/'pipeline.exit').write_text('1\n');(r/'PIPELINE-ERROR.txt').write_text(traceback.format_exc());raise
