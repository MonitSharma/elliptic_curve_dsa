# Preserved initial v16 coordinate failure

The first local description run exited1 at its independent target-coordinate
assertion before writing a proposal or launching a server job. It interpreted
the source c5 AND as `C5 = old[29] + acc0 + Nm0`. The source `maj_wire` convention
instead has `C5 = old[29] + C4`, because its product operands are
`acc4+C4` and `acc0+Nm0+C4`.

The corrected source coordinate then passes the complete262,144-row target
identity and the separate two-product algebra. The failure does not invalidate
the previously verified v13 arithmetic contract; the v16 initial local
proposal itself failed and is not counted as passing evidence.
