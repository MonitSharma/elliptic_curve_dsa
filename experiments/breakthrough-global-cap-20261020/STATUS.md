# Global budget experiment failed generation

The unchanged control reproduces complete raw `13f6ffc3`. Setting the
original walk planner's budget to 1,233 hits its existing capacity assertion
at forward step 130: fold room 15 versus modeled need 36, shed block 14 plus
two top wires and at most four internal finalization wires. The candidate
generation exits 101. There is no complete candidate or resource result.

The assertion remains intact. A separate experiment models the independently
verified helper reduction in preflight, with tight-budget native controls
before repeating full generation. Arithmetic cuts and iteration limits stay
fixed. This failure is not a declared final statistical-gate verdict.
