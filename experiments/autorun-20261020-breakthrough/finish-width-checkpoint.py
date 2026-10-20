from pathlib import Path
import re
r=Path(__file__).resolve().parents[2];e=r/'experiments';a=e/'autorun-20261020-breakthrough'
old='''valid; full point-add equivalence is not established. A predeclared512x64
development comparison now tests the frozen raw streams with full output,
phase, cleanup and protected scalar controls. This is not a final gate.'''
new='''valid; full point-add equivalence is not established. Predeclared512x64
development comparison completed with8 protected scalar batches per source:
same57 value-failing shot IDs, dirty0, other registers equal; both narrower
streams differ on14 target lanes already failing in both. Phase failures
45/32/37 and failed batches61/60/67 differ. No equivalence or final gate.
Paired rawT increments651.91(SE4.45) and1393.50(SE4.57) are diagnostic.'''
for p in [a/'checkpoint-width-index.patch',a/'DEVELOPMENT-NOTES.md',a/'LOG.md',r/'docs/research-plan.md',r/'docs/results-status.md',r/'docs/AGENT_HANDOFF.md']:
 raw=p.read_bytes();o=old.encode();n=new.encode()
 if p.suffix=='.patch':o=o.replace(b'\n',b'\n+');n=n.replace(b'\n',b'\n+')
 if o not in raw:o=o.replace(b'\n',b'\r\n');n=n.replace(b'\n',b'\r\n')
 assert raw.count(o)==(3 if p.suffix=='.patch'else 1),p;raw=raw.replace(o,n)
 if p.suffix=='.patch':
  delta=new.count('\n')-old.count('\n');raw=re.sub(rb'(@@ -\d+,\d+ \+\d+,)(\d+)( @@)',lambda m:m[1]+str(int(m[2])+delta).encode()+m[3],raw)
 p.write_bytes(raw)
p=e/'breakthrough-sparse-polynomial-20261020';(p/'STATUS.md').write_bytes(b'# Sparse Boolean-polynomial proof: correct, small saving\n\nThree native controls pass: scalar Boolean-ring identities, immutable overflow and48 guarded random measurement circuits across1024 inputs, full values/phase. Frozen stream audit takes210.5 seconds and finds one extra classically weighted half-Toffoli saving beyond truth14. Native count810868 to810867; diagnostic weight762345.25 to762344.75; width1233. Stream f84e09164ad5ed6f2ffd7d4b1f8843cde9fdc2a1edbb89d7a07eb95cd9a1d4b5. This is not a scored resource improvement. All38 evidence members verify locally.\n')
p=e/'breakthrough-width-correctness-20261020';(p/'STATUS.md').write_bytes(b'# Paired raw-width diagnostic: output equality not established\n\nLabel breakthrough-width-layout-development-v1,512x64 shots/source,4workers and8 protected scalar batches each. Raw1234/1233/1232 have57 identical value-failing shot IDs, zero dirty shots and equal other registers. Both narrower streams differ on14 target lanes already value-failing in both. Phase failures45/32/37; failed batches61/60/67. All mismatches and per-lane output hashes retained. This is development evidence versus historical raw control, not the current optimized public parent or a final gate. No scored improvement, nonce, unchanged benchmark or universal equivalence claim. All23 evidence members verify locally.\n')
for name in ['breakthrough-local-budget-20261020']:
 p=e/name;(p/'.gitattributes').write_bytes(b'* -text\n');(p/'.gitignore').write_bytes(b'/observer/\n/evidence.tar.gz\n');(p/'STATUS.md').write_bytes(b'# Physical fold cap with original global replay budget: active\n\nKeep global replay budget1234; the exact fold scheduler reads the smaller physical hard cap. Original preparation failed because a module-import uniqueness assertion also matched nested native test modules. The original source and failure log remain; v2 scopes insertion to the first module import and reuses the unfinished detached worktree before any source freeze. Native controls and complete generation are running. No gain, unchanged predicates or full correctness claimed.\n')
print('Completed diagnostics documented; active follow-up preserved.')
