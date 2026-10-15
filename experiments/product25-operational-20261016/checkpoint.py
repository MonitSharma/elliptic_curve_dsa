from pathlib import Path
import datetime,hashlib,json,os,tarfile
root=Path(__file__).resolve().parent
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
dest=root/'checkpoints'/stamp;dest.mkdir(parents=True)
files=[]
for p in root.iterdir():
 if p.is_file() and p.suffix in ['.py','.rs','.sh','.json','.log','.pid','.exit','.md'] and p.name!='manifest.json':files.append(p)
for p in (root/'tool').rglob('*'):
 if p.is_file() and 'target' not in p.relative_to(root/'tool').parts and (p.suffix=='.rs' or p.name in ['Cargo.toml','Cargo.lock']):files.append(p)
manifest={}
for p in files:
 data=p.read_bytes();relative=p.relative_to(root);out=dest/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);manifest[str(relative)]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
progress=[json.loads((root/f'worker{lane}-progress.json').read_text()) if (root/f'worker{lane}-progress.json').exists() else None for lane in range(4)]
lower_prefix=min((r['cumulative_worker_rows']//4096*4+lane if r else lane) for lane,r in enumerate(progress))*4096
streams=[]
for lane in range(4):
 p=root/f'worker{lane}.jsonl';size=p.stat().st_size if p.exists() else 0
 item={'path':str(p),'observed_bytes':size,'active_stream_not_copied':True}
 if size:
  with p.open('rb') as f:
   first=f.read(min(size,4*1024*1024));f.seek(max(0,size-4*1024*1024));last=f.read(min(size,4*1024*1024))
  item.update(first_up_to4MiB_sha256=hashlib.sha256(first).hexdigest(),last_up_to4MiB_sha256=hashlib.sha256(last).hexdigest())
 streams.append(item)
record={'status':'LIVE_RESEARCH_CHECKPOINT_NOT_A_PASS_OR_RECORD','created_Singapore':stamp,'progress_atomic_snapshots':progress,'completed_unique_rows':sum(r['cumulative_worker_rows'] for r in progress if r),'complete_lower_nonce_prefix':lower_prefix,'active_streams':streams,'source_and_snapshot_files':manifest,'selected_nonce':None,'submission_mode':'queue'}
(dest/'CHECKPOINT.json').write_text(json.dumps(record,indent=2)+'\n')
archive=root/'checkpoint-evidence.tar.gz'
with tarfile.open(archive,'w:gz') as out:out.add(dest,arcname=stamp)
receipt={'checkpoint':str(dest),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(manifest)+1,'completed_unique_rows':record['completed_unique_rows'],'complete_lower_nonce_prefix':lower_prefix,'not_a_resource_record':True}
(root/'checkpoint-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
