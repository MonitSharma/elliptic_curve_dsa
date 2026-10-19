# Why a guard-support release is exact

For each logical quantum wire q, maintain an upper bound S on the classical
conditions under which its basis value may be one: q ⇒ S. This statement is
for every input assignment and every sequence of measurement outcomes.
It uses no failure-rate sample or selected input packet.

Registered quantum inputs start with S=true. Other wires start in zero and
have S=false. Classical values are immutable Boolean-function nodes; updating
a classical bit changes its pointer, while a captured Push condition keeps its
old node. The Boolean constructors implement exact AND, NOT, XOR and selection.
A complexity cut becomes a fresh opaque function with recorded arguments.
Treating such a function independently can only lose relations.

The value-support induction uses these conservative bounds for execution F:

- X on t: S(t) becomes S(t) OR F.
- CX a→t: add S(a) AND F to S(t).
- CCX a,b→t: add S(a) AND S(b) AND F to S(t).
- R/Hmr on t: its new value is old(t) AND NOT F. An old DNF term can be
  discarded when it implies F. Other terms can remain unchanged safely.
- A conditional swap retains each old support and adds the other support
  intersected with F. An unconditional swap exchanges the supports exactly.
- Phase and classical operations do not change quantum values.

DNF conjunction distributes terms and removes contradictory literals. OR drops
subsumed terms. If the representation exceeds 16 terms or 32 factors, it becomes
true. Each operation therefore preserves q ⇒ S. When S is false, q is exactly
zero on every assignment. This qubit is unentangled and its physical lane can
be reused. The capped representation never turns an unknown into zero.

Before each emitted operation, every referenced logical role has a distinct
physical lane; absent roles are known zero and receive clean lanes. The gate
keeps its original kind, classical fields, and scope. Afterward, lanes are
released only for roles with S=false. All R and Hmr events, including inactive
events, remain in their original order and consume the same RNG words. Phase
kickback happens before the release, so it is preserved along with values.
Final swaps restore all registered output roles to their annotated positions.
The detached identity tail is then restored without modification.

Thus the emitted circuit is a relabeling of the same evolution, with clean
workspace reuse. It retains every original Toffoli and execution condition;
its extra final swaps have zero Toffoli cost. Exhaustive constructor/support
controls and protected-simulator integration tests check the implementation.
A new public-record claim still requires the prescribed complete benchmark
and independent statistical qualification.
