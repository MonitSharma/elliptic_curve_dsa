# Exact full-RNG value prefilter — correctness passes, speed experiment negative

This research-only follow-up uses the independently certified reduced value
program while preserving the original product circuit's complete Fiat transcript
and every measurement draw. A wrong scored coordinate is an exact rejection;
value-passing lanes fall back to the original value/phase/ancilla interpreter.
No global RNG-independence theorem is assumed. No circuit or score is changed.

All quantum and classical words match the original full simulator on the128-nonce
shadow run, every batch of the known positive control, and the partial11-nonce
range. All1024 fixed nonce decisions and witness batches match the pinned
original integrated screen. The known positive nonce1046072871510 passes all141
batches and the protected9024-shot replay with zero failures in all channels.

The fixed three-trial interleaved comparison does not improve speed: median
6.331904 seconds for the original versus7.139731 for this follow-up, using16
workers on1024 nonces. Measurement SHAKE remains the dominant cost. The result
does not replace the existing screen or authorize an unaffordable search.

The initial launcher missed the Rust environment. A subsequent static analysis
incorrectly initialized classical input-register bits to known zero; full-state
shadow validation caught it before timing/search. Both attempts are preserved.
The corrected analysis marks all input-register classical wires unknown and
retains measurement-word positions even when a guarded operation is dead.

Original source SHA256:2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e.
Reduced compact SHA256:a4d01570c76b589ed5d2d59b79ac12ccb4a7a155f1f70d415e3c5da2e5935927.
RESULT.json contains all six timings. Source and logs are archived; executable
and shared-library hashes are in frozen.sha256. No nonce search or submission.
