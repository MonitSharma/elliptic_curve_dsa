# Accepted-source cost and live-workspace audit

Completed observation-only audit; no new candidate or score. The observer's
entire compressed stream exactly matches official d9ae2845:
125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501.
All17 protected files are unchanged. Three phase-mapper controls and two replay
controls pass;8 fresh batches match every protected scalar quantum/classical
wire, phase, RNG draw and executed-Toffoli count. All512 diagnostic rows match
the unchanged original replay binary exactly, including failing inputs.

On512x64 fresh labelled shots, measured mean executed costs are division
358252.50 (47.07%), multiplication362703.79 (47.66%), square39491.01 (5.19%).
These diagnostic means are not submitted scores. Every regional sum equals
the exact total. There are62 value-failing shots,38 phase-failing shots and
zero dirty shots in this baseline sample; it is not a final statistical gate.

The first build-time peak is1234 in division. Its nine owner groups include
206 decision-history qubits and134 carry qubits. This is ownership evidence,
not a lower bound or a reduced-width implementation. WORKSPACE-OWNERS.json
and EXECUTED-COST-PROFILE.json retain the exact breakdown.

The65-member evidence.tar.gz and every included file hash were verified
locally. Full operation streams remain server-retained with hashes. Runtime,
source patch, added source, tests and original replay comparison are bound in
the archive. Raw server process arguments were excluded from public evidence.
