# Restricted q23 owner and payload capacity

The candidate funds q23 on `sc.sw` only in a pure-HR source envelope. It
excludes HT, switching, done, delayed/no-step and incoming switched layouts,
the exceptional tt column, and the wide first column. The first column uses
`sc.sw` as the ninth SZ bit and cannot lend it. The guard also requires
`SYmax+23<128`, so the parked q23 destination remains inside Q.

The HR cycle puts `sc.sw` last. A preposition record moves q23 into
Q[SY+23] before V and clears its owner; the ordinary park skips that bit.
After V, the involution returns q23 to its owner for the correction that
consumes it. Payload padding and compare/carry scratch exclude `sc.sw` in
these admitted pure-HR columns. Its lifetime ends before map/switch logic.

K32's small-SY predicate now ends at97, so even QB24's largest parked bit
is at120 and Q121–Q127 remain zero. Large98–128 gives SZ<=159, within the
tested low-six SZ donor interval. Mixed and crossing quotient loops keep
their23-bit cap. Payload digit capacity becomes24 globally because its
`KE` follows `pointadd_frogdrop::QB`; otherwise a24-bit digit would still
fail despite the newly funded quotient owner. The fixed13-lane middle pool
does not grow with that constant.

Two native tests completed with exit0. The q23 preposition test covers256
cases, SY97/98/104 boundaries, arbitrary259 passengers, all-wire arithmetic
and inverse restoration and zero phase. It is unitary and has zero
measurement coefficients. The exact shot8048 division2 column24/Euclidstep25
test covers256 admitted payload states, including dy0,1,p−1, r24−1 and varied
inputs. It passes the exact Euclid/payload/scratch oracle, all-wire inverse
restoration and zero sampled native phase. Maximum exercised payload digit
is8,505,374, so the24th digit bit is tested. Native runtime1.38s.

Independent measurement coefficients for the complete column are unassessed.
Prior crossing/payload regressions are recorded separately. No unchanged full
benchmark has been run on this source, no global QB24 ownership is claimed,
and no complete point-addition or Q692 record follows.

The four changed source files and hashes are in
`candidate-cap24-purehr-manifest.json`. Candidate patch SHA256:
`502cc984d80a1323c66764b9c3c627611946c103d5f693d15f30337d659c7b07`.
The harness, Cargo/toolchain and preserved compact submission are unchanged.
