from pathlib import Path
import json,shutil,hashlib
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016');r.mkdir(exist_ok=True)
pref=r.parent/'prefilter-20261015/tool';tool=r/'tool';(tool/'src').mkdir(parents=True,exist_ok=True)
shutil.copy2(pref/'Cargo.toml',tool/'Cargo.toml')
source=(pref/'src/main.rs').read_text().split('include!("slice.rs");')[0]
(tool/'src/main.rs').write_text(source+'\nmod observed;\ninclude!("body.rs");\n')
protected=r.parent/'overnight-20261014/product-b3-baseline/src/sim.rs'
s=protected.read_text().replace('use crate::circuit::','use quantum_ecc::circuit::').replace('use ruint::aliases::U256;','use alloy_primitives::U256;').replace('crate::circuit::','quantum_ecc::circuit::').replace('Simulator','ObservedSimulator')
s=s.replace('pub phase: u64,','pub phase: u64,\n    pub trace: Vec<(usize,u64)>,')
s=s.replace('phase: 0,','phase: 0,\n            trace: Vec::new(),')
s=s.replace('ops: impl Iterator<Item = &\'b Op>)','ops: impl Iterator<Item = &\'b Op>, marks: &std::collections::BTreeSet<usize>)')
s=s.replace('for op in ops {','for (index,op) in ops.enumerate() {')
s=s.replace('\n        }\n\n    }\n\n    /// Writes','\n            if marks.contains(&(index+1)) {self.trace.push((index+1,self.phase));}\n        }\n\n    }\n\n    /// Writes')
(tool/'src/observed.rs').write_text(s)
shutil.copy2(r/'body.rs',tool/'src/body.rs')
rows=[json.loads(l)for l in(r.parent/'precision-family-20261016/fresh-paired/parent.jsonl').read_text().splitlines()]
fail=[dict(batch=row['batch'],**f)for row in rows for f in row['failures']if f['phase']and not f['value']and not f['dirty']]
(r/'phase-only-witnesses.json').write_text(json.dumps(fail,indent=2)+'\n')
(r/'witnesses.tsv').write_text(''.join(f"{i}\t{f['k1']}\t{f['k2']}\n"for i,f in enumerate(fail[:64])))
marks={0,11630716};labels={}
folds=json.loads((r.parent/'precision-repair-20261016/surviving-folds.json').read_text())['rows']
for f in folds:
 if not f.get('found'):continue
 a=f['final_start'];b=a+f['ops'];marks.update([a,b]);labels.setdefault(a,[]).append(['fold-start',f['reverse'],f['tick']]);labels.setdefault(b,[]).append(['fold-end',f['reverse'],f['tick']])
for name in['complete-helper-proof-spans.tsv','phase-lifetime-proof-spans.tsv','expanded-lifetime-proof-spans.tsv']:
 for line in(r.parent/'prefilter-macro-20261016/additional'/name).read_text().splitlines():
  if not line.strip():continue
  a,b=map(int,line.split()[:2]);marks.update([a,b]);labels.setdefault(a,[]).append([name,'start']);labels.setdefault(b,[]).append([name,'end'])
(r/'marks.txt').write_text(''.join(f'{i}\n'for i in sorted(marks)))
(r/'mark-labels.json').write_text(json.dumps(labels,indent=2)+'\n')
(r/'source-hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in[protected,pref/'Cargo.toml',pref/'src/main.rs',tool/'src/observed.rs',tool/'src/main.rs',tool/'src/body.rs']},indent=2)+'\n')
print('phase-only shots',len(fail),'marks',len(marks))
