# Exact carry encoding and decoded readers

Let a,b,c be the three values before a carry constructor and t initially zero.
The carry is M=ab XOR ac XOR bc. The three-gate in-place constructor

    CX(b,a); CX(b,c); CCX(a,c,b)

stores A=a XOR b, B=M, C=c XOR b. Write u=A*C. Then

    a = A XOR B XOR u
    b = B XOR u
    c = C XOR B XOR u
    t = B

These are the **body** operand values for the six-gate restored constructor.
For the four-gate compact constructor the detector swaps its a/b role names
(see old opening()). Its body values are a XOR c and b XOR c, so instead

    body_a = A XOR C
    body_b = C
    body_c = C XOR B XOR A*C
    body_t = B

Thus compact-cell reads of body_a/body_b are linear. A CNOT query into an
external target expands to CNOTs and at most one CCX. Multiply decoded control
polynomials for a CCX query: emit only if square-free ANF degree <=2. Phase
queries expand to Z/CZ/CCZ when degree <=3. Copy the original direct condition
and keep its captured scope. Source targets must be outside a,b,c,t.

Two full-cell products simplify without cubic terms:

    a*b = B XOR A*B
    b*c = B XOR B*C
    a*c = B XOR A*B XOR B*C

This permits additional phase reads at zero T cost. Any outside-variable term
of degree three in an XOR-target query is unsupported in the first version;
do not silently introduce a new ancilla or an unproved multi-control gate.

The final three-gate cleanup

    CCX(A,C,B); CX(B,C); CX(C,A)

restores b,c and writes a XOR b XOR c into a. It matches the original sum
cleanup in both detector role conventions. Body operands must remain read-only.
Do not compose nested borrowed encodings with the first reader implementation.

The removed Hmr/private-phase correction cancels exactly for all outcomes when
the original matching pattern and stable operand conditions hold. Preserve the
existing private-bit suffix proof, exclude registered classical destinations,
and validate an explicit injection from remaining RNG events to source events.
Original and candidate unregistered private classical garbage may differ;
all quantum outputs, phase, registered classical inputs and future behavior
must agree. Ordinary final qualification still uses the protected physical RNG.
