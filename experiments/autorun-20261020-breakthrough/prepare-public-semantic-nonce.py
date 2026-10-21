from pathlib import Path
import subprocess
a=Path(__file__).resolve().parent;ex=a.parent;r=ex/'breakthrough-public-semantic-nonce-20261021';r.mkdir(exist_ok=False)
s=(ex/'breakthrough-de8-repeat-nonce-20261020/run.py').read_text().replace('breakthrough-de8-repeat-finished-20261020','breakthrough-public-semantic-finished-20261021').replace('breakthrough-de8-repeat-final-gate-20261020','breakthrough-public-semantic-final-gate-20261021').replace('cache-repeat-generic-final-20261020-v1','public1829-exact-semantic-final-20261021-v1')
s=s.replace('Ascending1..65536 in64-nonce windows','Ascending1..16777216 in128-nonce windows').replace("'65536','8'", "'16777216','16'").replace("'UNUSED','64'", "'UNUSED','128'")
s=s.replace("'unique_nonce_controls':8,'control_scalar_batches':24", "'workers':16,'declared_first_nonce':1,'declared_maximum_nonce':16777216,'window':128,'unique_nonce_controls':8,'control_scalar_batches':24")
s=s.replace('import hashlib,json,os,subprocess,time','import hashlib,json,os,subprocess,time,shutil,socket')
at=''' assert socket.gethostname()=='LHC-104-070';available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024**2
 (r/'resource-preflight.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'cpus':os.cpu_count(),'available_kib':available,'workers':16,'library_threads':1,'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{x:shutil.which(x)for x in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,comm,pcpu,rss','--sort=-pcpu']).decode()},indent=2)+'\\n')
'''
s=s.replace(" start=time.time()",at+" start=time.time()",1)
(r/'run.py').write_text(s);compile(s,str(r/'run.py'),'exec');(r/'.gitignore').write_text('tool/\ntarget/\n__pycache__/\n*.jsonl\n');(r/'.gitattributes').write_text('* -text\n');(r/'PLAN.md').write_text('# Frozen semantic product candidate nonce search\n\nOnly candidate own final32768x64 PASS permits this original engine. Unchanged qualified full-state/RNG/curve engine; fresh source-bound8control nonces1..8/24protected fullstate batches at0,70,140. ORIGINAL_FS input membership and seed bytes checked. Ascending1..16777216,128noncewindows,16workers, lowestPASS, every screen/overrun retained. No arithmetic or value prefilter in this version. Additional selected complete9024 protected replay and unchanged benchmark mandatory. This is a new passed frozen source, never a resumption of the retired OLD6192 search. No table/cut/circuit changes or choosing by T.\n')
launch='''import json,subprocess
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/breakthrough-public-semantic-nonce-20261021');assert not(r/'run.pid').exists()
with(r/'run.log').open('xb')as out:p=subprocess.Popen(['nohup','python3','-u',str(r/'run.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\\n');print(json.dumps({'pid':p.pid,'root':str(r)}))
''';(r/'launch.py').write_text(launch)
subprocess.run(['ssh','-o','BatchMode=yes','smu_server','mkdir','/home/hclau/ecdsa_research/'+r.name],check=True)
for n in ['run.py','launch.py']:
 subprocess.run(['scp','-o','BatchMode=yes',str(r/n),'smu_server:/home/hclau/ecdsa_research/'+r.name+'/'+n],check=True)
out=subprocess.check_output(['ssh','-o','BatchMode=yes','smu_server','python3','/home/hclau/ecdsa_research/'+r.name+'/launch.py'],text=True);(r/'SERVER-LAUNCH.json').write_text(out);print(out)
