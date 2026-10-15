from pathlib import Path
import shutil
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016')
tool=root/'census-tool';(tool/'src').mkdir(parents=True,exist_ok=True)
previous=root.parent/'payload-model-20261016/cut-tool'
for name in ['prefix.rs','observed_sim.rs']:
    shutil.copy2(previous/'src'/name,tool/'src'/name)
text=(previous/'Cargo.toml').read_text().replace('product_paired_diagnostic','production_fold_census')
(tool/'Cargo.toml').write_text(text)
shutil.copy2(previous/'Cargo.lock',tool/'Cargo.lock')
shutil.copy2(root/'census.rs',tool/'src/main.rs')
print('Prepared source-bound fold census; not compiled or launched')
