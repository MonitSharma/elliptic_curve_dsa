# Constructor and four consumer writes

The new [v13 contract](consume-four-analysis-v13.json) consumes all Q correction
fields into the accumulator's low ten bits. It retains U0..6, sign, H0..6,
low_result0..9 and carry10. The original source uses35 ANDs. All26 scalar
outputs match independent integer arithmetic on every262,144 assignment to
the18 primitive inputs. Raw rank is19 and target-inclusive rank43, giving a
necessary24-AND value bound, with attainability unresolved.

The [v14 family](consume-four-aux-v14-summary.json) considers every153 product
of distinct raw coordinates. One lies in the target span; the152 distinct
outside cosets each yield rank44/25-AND candidate interfaces. Every selected
interface closes with trusted affine-product UNSAT, with no unknown.

The [v15 family](consume-four-subspaces-v15-summary.json) selects seven of the
11 independent auxiliary directions from the original source span: TT, R1,
R2, R3, Y3, Y4, Y5, C6 and Y16 gates4..6. All330 selected rank50 interfaces,
each with a31-AND value budget, close negatively. These are coordinate
subspaces, not every linear subspace of the original span or every possible
outside function. No complete31-AND constructor-and-consumer witness follows.

The [v16 identity](consume-four-carry-pair-v16-description.json) follows a
specific changed bit5 obligation. Let u=acc0, v=Nm0, a=acc4, c=C4. Then

`C5+R1=(u+a+c)*(v+a+c)+a*c+a+c`.

All262,144 rows independently verify both the source carry coordinate and
the changed output coordinate. The auxiliary a*C4 lies outside the complete
original source span. Two products give an exact six-AND prefix in a new
rank44 interface. Its [completion query](consume-four-carry-pair-v16-summary.json)
nevertheless returns trusted affine-product UNSAT at that prefix; it is a
positive partial identity, not a complete replacement. An initial local
majority-wire offset mistake was rejected before a proposal or server job;
its [failure](consume-four-carry-pair-v16-preparation-failure.md) is preserved.

All server jobs finish with exit zero, one core and a2GiB memory limit. Raw
receipts preserve source/data hashes, exact selected interfaces, solver
statuses, settings, PID/exit and logs. There are no saved formal solver proof
certificates. Primitive producer admission, arbitrary higher quantum words,
measurement cleanup/phase, physical schedule/width and full executed cost
remain separate obligations. No qualified circuit score is claimed.
