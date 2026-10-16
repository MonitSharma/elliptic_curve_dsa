"""Replace only unlaunched census watchers, preserving their original protocol."""
from pathlib import Path
r=Path(__file__).resolve().parent
exe='/home/hclau/ecdsa_research/simd-census-20261016/bin/simd_census_v1'
digest='49d99d2bf380b628550c3ed979b5bf2adfc1a962fb6fd00a5df267cde853f554'
for name in ['product25','category']:
    old='run-product25-census.sh' if name=='product25' else 'run-category-census.sh'
    s=(r/old).read_text()
    folder='product25-frozen-census-20261016' if name=='product25' else 'category-restore-census-20261016'
    newfolder=folder.replace('-20261016','-v2-20261016')
    s=s.replace(folder,newfolder)
    oldexe='exe=/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census'
    assert s.count(oldexe)==1
    check=f'''exe={exe}
printf '%s %s\\n' {digest} "$exe" | sha256sum --check > "$out/executable-check.txt"
'''.rstrip()
    s=s.replace(oldexe,check)
    assert s.count('census.jsonl" >')==2
    s=s.replace('census.jsonl" >','census.jsonl" 0 >')
    summary='summarize_product25_census.py' if name=='product25' else 'summarize_category_census.py'
    newsummary=summary.replace('.py','_v2.py')
    s=s.replace(summary,newsummary)
    if name=='category':
        s=s.replace('test "$(cat category-restore-20261016/launcher.exit)" = 0','test "$(cat category-restore-20261016/launcher.exit)" = 101\nwhile [ ! -f category-restore-20261016/baseline-check.exit ]; do sleep 30; done\ntest "$(cat category-restore-20261016/baseline-check.exit)" = 0')
    (r/old.replace('.sh','-v2.sh')).write_text(s,newline='\n')
    (r/newsummary).write_text((r/summary).read_text().replace(folder,newfolder),newline='\n')
