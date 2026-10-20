# Verification-only value IR, independent of candidate and nonce inputs

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

V2 independently freezes new verification tool: up to2048 rounds and exact
read/write commutation. Identical guarded involutions may cancel across gates
that only read their common controls; every target must have no intervening
read/write, and controls no intervening write. Linked prior-touch/prior-write
records skip cancelled nodes. Eighth protected exhaustive native control covers
shared read-only controls, target reads and control writes. No nonce rejection
or quantum candidate/resource score. Prior32-round audit stays unchanged.
