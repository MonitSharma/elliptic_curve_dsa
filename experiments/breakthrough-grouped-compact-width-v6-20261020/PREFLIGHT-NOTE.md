The initial local one-line preparation command had a quoting syntax error and
made no source change. Its dependent generator and remote launcher rejected
the missing run.py. Only the intended scope document had been transferred.
The dedicated prepare-compact-unitary-tail-v6.py replaces that failed local
preflight and validates the generator before writing source. No source freeze,
semantic test, workload, statistical gate or nonce ran in the failed preflight.
