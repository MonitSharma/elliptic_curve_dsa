from pathlib import Path
import json,datetime,shutil,hashlib
r=Path('/home/hclau/ecdsa_research/n2-loan-retention-20261016');d=r/'all-retained-cap8';assert not d.exists()
decl=dict(status='PREDECLARED SOURCE-ONLY WIDTH COST AUDIT; NO SAMPLING',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_family='ALL N2 loans retained; no clean-loan premise',extra_scoped_capacity=8,scope='both complete source n2_div_batch and n2_mul_batch calls',reason='exactly compensate eight held original rail bits; no minimal-width sweep or scored packet used',no_table_or_allocator_anchor_bypass=True,no_native_or_record_claim=True)
(r/'ALL-RETAINED-CAP8-PREDECLARATION.json').write_text(json.dumps(decl,indent=2)+'\n')
shutil.copytree(r/'all-retained',d,ignore=shutil.ignore_patterns('.git','target'))
p=d/'src/point_add/leapfrog.rs';s=p.read_text()
for name in ['n2_div_batch','n2_mul_batch']:
 needle=f'        {name}(c, &mut wk, &mut pay);';assert s.count(needle)==1
 s=s.replace(needle,f'        let retained_cap=cells::cap()+8;\n        super::pingpong::with_phase_cap(Some(retained_cap),||{name}(c,&mut wk,&mut pay));')
p.write_text(s)
(r/'all-retained-cap8-source.json').write_text(json.dumps(dict(files={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(d/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
