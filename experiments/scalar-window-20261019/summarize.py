import json,statistics
from pathlib import Path
r=Path(__file__).resolve().parent
rows={k:json.loads((r/(k+'.json')).read_text()) for k in ['frozen-20','extended-20','extended-22','extended-24']}
reference=rows['frozen-20']['output_sha256'];assert all(v['output_sha256']==reference for v in rows.values())
med={k:statistics.median(v['times_seconds']) for k,v in rows.items()}
result={'status':'ALL_EXACT_WINDOW_VARIANTS_MATCH_FRESH_PUBLIC_POINTS','fresh_pairs_per_variant':655360,'median_seconds':med,'median_speedup_vs_frozen20':{k:med['frozen-20']/v for k,v in med.items()},
 'peak_rss_kib':{k:v['peak_rss_kib'] for k,v in rows.items()},'startup_seconds':{k:v['startup_seconds'] for k,v in rows.items()},
 'scope':'Component-only scalar preparation timing. End-to-end prefixes, source-specific full qualification and actual multiworker memory admission remain mandatory; no production recommendation or resource score.'}
(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
