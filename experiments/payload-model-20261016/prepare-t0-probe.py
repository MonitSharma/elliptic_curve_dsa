from pathlib import Path
import shutil,tarfile
p=Path('/home/hclau/ecdsa_research/payload-model-20261016');base=p/'observer-tip/src/point_add'
assert (p/'observer.exit').read_text().strip()=='0'
with tarfile.open(p/'observer-v1-source.tar.gz','w:gz')as t:
 t.add(base,arcname='src/point_add')
for name in ['build.log','build.exit','observer.log','observer.exit','stream.sha256']:
 shutil.copy2(p/name,p/('v1-'+name))
q=base/'leapfrog.rs';s=q.read_text();assert 'payload_model_probe'not in s;s+='\n'+(p/'t0_probe.rs').read_text();q.write_text(s)
q=base/'mod.rs';s=q.read_text();needle='pub fn build() -> Vec<Op> {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    let model_probe=std::env::var_os("PAYLOAD_MODEL_PROBE").is_some();');needle='    let mut ops = build_point_add();';assert s.count(needle)==1;s=s.replace(needle,'    if model_probe{leapfrog::payload_model_probe();std::process::exit(0);}\n'+needle);q.write_text(s)
print('Prepared source primitive probe; normal branch unchanged')
