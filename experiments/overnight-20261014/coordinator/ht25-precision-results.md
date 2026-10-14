# Quotient storage and reciprocal precision are separate blockers

The fixed N275-v2 official packet is unchanged: SHA256
`bdba0f9ac464903dc9838cc2c05f7120f31941937226167f0a406e122dd4ec7d`.
An ideal-model audit independently replays both divisions of all9024points,
for18048divisions per precision variant. The source change is an asserted
model-only substitution: HT capacity25, with ordinary mixedHR22/pureHR24,
small-SY cutoff95, small head32 and crossing reserve9. The preserved model and
the substituted model both have exact hashes in `ht25-ideal-packet.json`.

At fixed shot2379/division2, a large head24 leaves a nonzero predicted HT
inverse quotient at columns86and87 (remaining3and1). Head25 clears those
events but leaves remaining1atcolumn88. Head32 leaves no predicted event on
either division of2379 or any other division in this fixed packet. Only that
one division is flagged for the head24and25 variants. Thus a storage-only
25-bit quotient prototype still has a separate precision failure to detect.

This model uses ideal unbounded Euclidean state at each step. It does not
propagate real gate/carry corruption, check source schedule admission, prove
physical donor availability, simulate measurement phase or qualify a point
addition. In particular, head32 passing this finite arithmetic model is not
an all-input proof or authorization for a full evaluation. The quantum owner,
source mask, delayed reserve and precision-lifetime obligations remain.

Script: `scripts/audit-ht25-ideal-packet.py`. Elapsed29.39seconds locally;
no server operation vector was allocated. No contestant, scorer, schedule,
nonce or test input changed.
