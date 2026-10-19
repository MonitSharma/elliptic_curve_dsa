# Combined exact schedules: negative resource screen

All three fixed stages finished with genuine run.exit=0. The compact scheduler
reproduces the previous complete permutation and output bytes exactly; its full
source run took 35.92 seconds instead of 7m14s. The annotation-only allocator
also reproduces its previous output and release-event hashes exactly.

Both tail-pinned combinations remain Q1234, with 85,462 conditional cleanups.
The ordinary case's output raw SHA3-256 is
4947fdcf4e9d5eecc6f63a04a94bc255ad5400a995779f474c9b74aaa99c8876;
the cleanup-prioritized case's is
ad1f9690c5790af2aeb6e7f26751f570b21d826dfcf8f75b48ee70e37ea8226e.
These are diagnostic generated streams, not scored results.

Thirty tool controls pass. Separate protected-simulator controls pass on both
complete combinations: each uses eight batches of 64 arbitrary raw assignments
and compares logical/permuted full transcripts, registered outputs, original
classical bits, phases, executed Toffolis, scratch-state multisets and RNG
continuation. Genuine controls.exit=0. No statistical gate or nonce search was
launched by this experiment; parent4's independent search is unchanged.

The next distinct method removes the global ordering constraint between
independent measurement/reset events, with an explicit labeled-outcome
bijection. That new circuit cannot claim equal ordinary physical-RNG coupled
transcripts and still requires the normal, unchanged qualification protocol.
