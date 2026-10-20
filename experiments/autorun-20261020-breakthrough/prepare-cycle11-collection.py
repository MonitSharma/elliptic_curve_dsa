from pathlib import Path
import ast
a=Path(__file__).parent;names=['breakthrough-value-ir-audit-v2-20261020','breakthrough-value-ir-audit-v3-20261020','breakthrough-value-ir-audit-v4-20261020','breakthrough-value-abstract-audit-20261020','breakthrough-dense-exact-verifier-20261020','breakthrough-public1829-reproduction-20261020','breakthrough-exact-witness-ripple-20261020']
for src,dest,terminator in[('seal-research-cycle10.py','seal-research-cycle11.py','\nws='),('collect-research-cycle10.py','collect-research-cycle11.py','\nsha=')]:
 s=(a/src).read_text();start=s.index('names=[');end=s.index(terminator,start);s=s[:start]+'names='+repr(names)+s[end:]
 if dest.startswith('seal'):
  needle=";(r/'TERMINAL-AUDIT.json').write_text";assert s.count(needle)==1;s=s.replace(needle,"\n if name=='breakthrough-public1829-reproduction-20261020':audit.update(status='EXACT_UNMODIFIED_OFFICIAL_PUBLIC_RECORD_BENCHMARK_REPRODUCTION',scope='Complete original9024benchmark/officialmetrics/stream reproduced without source/harness changes; existing public record, not our newcandidate.')\n (r/'TERMINAL-AUDIT.json').write_text")
 ast.parse(s);(a/dest).write_text(s)
print('Seven completed fronts, including exact public reproduction and original pre-freeze failure selected.')
