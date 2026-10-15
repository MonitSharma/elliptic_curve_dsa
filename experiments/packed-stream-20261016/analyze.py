from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parent;old=root.parent/'packed-witness-20261016'
def rows(p):return {r['nonce']:r for r in map(json.loads,p.read_text().splitlines())}
report={}
for name in ['shadow128','timing-t2','timing-t16','partial']:
 a=rows(old/(name+'.jsonl'));b=rows(root/(name+'.jsonl'));assert a==b,(name,'every witness/shot and provisional status must match')
 assert all(r['authoritative_rejection'] is False and r['proof_accepted'] is False for r in b.values())
 text=(root/(name+'.log')).read_text();fields=dict(re.findall(r'(\w+)=([0-9.]+)',text))
 report[name]={'rows':len(b),'timing':fields,'same_all_rows_as_prior_packed':True}
out={'status':'STREAMED_FIAT_INPUTS_PACKED_BENCHMARK_PASS_REJECTION_DISABLED','original_source_sha256':'2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e','runs':report,'proof_accepted':False,'authoritative_rejections':0,'nonce_selected':False,'nonce_search':False,'resource_record':False}
(root/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
