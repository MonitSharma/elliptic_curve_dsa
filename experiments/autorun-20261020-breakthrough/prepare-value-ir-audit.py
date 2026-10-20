from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-value-cone-audit-v2-20261020';r=a.parent/'breakthrough-value-ir-audit-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
shutil.copyfile(a/'value-ir-audit.rs',r/'audit.rs')
s=(old/'run.py').read_text().replace('value_cone_audit','value_ir_audit').replace("test result: ok. 4 passed; 0 failed;","test result: ok. 7 passed; 0 failed;")
s=s.replace("'publicacd0':(ws/'breakthrough-public-acd0-reproduction-20261020/parent/ops.bin','3d7c94f1dea887dd2d4ff13326e350756350cc1044d396444c3f820f8bfad827')","'product_candidate':(ws/'breakthrough-public-best-drop-finished-20261020/candidate/ops.bin','6192778816154b713a714446b3e7d28165a649460173a3e3f17d9de06fa7bb96')")
s=s.replace("'scope':'Read-only conservative output-value dependency audit with classical SSA/captured guard versions. Four native value/guard/RNG/fault controls before full stream audits. No rewritten candidate, nonce screening/rejection, correctness gate, benchmark or score.'","'scope':'Verification-only value IR with guarded-write dominance zero certificates, captured classical SSA, liveness and untouched-participant equal-guard involution cancellation. Seven protected native value/guard/reset/RNG/fault controls before fixed stream audits. Initial registered quantum inputs arbitrary, helperszero. Phase omitted: this is NEVER a quantum candidate or resource score. No nonce screened/rejected; any future filter needs separate exact protected qualification.'")
s=s.replace("'native_controls':4","'native_controls':7").replace('READONLY_VALUE_CONE_AUDIT_COMPLETE_NOT_A_CANDIDATE_OR_NONCE_SCREEN','VERIFICATION_ONLY_VALUE_IR_AUDIT_COMPLETE_NOT_A_QUANTUM_CANDIDATE_OR_NONCE_SCREEN');ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Verification-only value IR, independent of candidate and nonce inputs

Do not submit this IR or call its gate counts quantum resource improvements.
It omits phase and can ONLY support a separately qualified wrong-output rejection
filter. The actual candidate/gate/official harness stay unchanged. No nonce is
screened or rejected by this audit.

Protected simulator semantics checked: HMR stores an independent random word
under captured/perop guard, updates only phase from the old qubit and resets its
value; R updates phase/resets value. All RNG positions consumed even under false
guards. Classical writes get unique SSA IDs; captured PushCondition uses the
old ID even after mutations. Model all quantum registered inputs as arbitrary,
other helperszero. Track an intersection of guard literals for every possible
nonzero write. Reset can be normalized to unconditional valuezero only when its
guard is implied by all possible nonzero writes, or the qubit is alreadyzero.
Classical HMR definitions retain their original guard and RNG index separately.

Then exact backward value liveness and self-inverse gate cancellation require
identical captured guard IDs and untouched quantum participants. Iterate to a
fixed point or32round limit. All transforms use only frozen source syntax, not
packet inputs/census outputs or historical predictors. Seven protected native
controls include full smallbasis/guards, prepared arbitrary nonoutput input,
dominated and non-dominated resets, captured mutation, changed perop guard,
genuinely live measurement/RNG position, and omittedreset fault detection.
Only after PASS audit frozen product61927788 and officialT71/278802f0 streams.
Native tests are not an exported quantum circuit or a benchmark score. A future
value filter must bind full original FS/source/tail and have independent full
protected point qualification before it may reject any nonce; PASS always needs
the original full-state engine and unchanged9024benchmark.
''');print(r)
