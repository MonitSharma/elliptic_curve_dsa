# The event mapping is part of the proof

Each primitive R or Hmr has a fixed source-event label. Its basis-state
transition is deterministic once its outcome word and execution condition are
given. An R and an Hmr both draw a word even if the execution condition is
false. The total event count therefore depends only on the fixed circuit.

The scheduler preserves all read/write conflicts on quantum wires and
classical bits, plus each captured-condition scope boundary. It may exchange
independent event nodes. For a swap of two such nodes, assigning each node its
own original labeled word preserves the complete values, classical results,
phase and cost. Their quantum/classical effects have no conflicting support.
Composing these adjacent commutations gives the complete permutation proof.

The exported RNGPERM1 file lists, for every new event position, its original
event ordinal. A separate check proves coverage and uniqueness, binds the
original stream hash, checks the complete operation permutation, and verifies
each event's ordinal against that permutation. The protected-simulator control
then supplies words through this explicit bijection and compares full states.
The allocator keeps the event sequence produced by the scheduler.

Consequently the exact labeled evolution agrees for every possible input and
every possible vector of event outcomes. For independent uniform outcome
words, their fixed permutation has the same joint distribution. This is the
channel-equivalence argument; it is not a claim that equal ordinary SHAKE
streams produce equal coupled transcripts after event reordering.

Actual qualification and scoring use the unchanged census driver and official
benchmark with ordinary physical-order SHAKE draws. The mapped-outcome control
is an implementation check and cannot qualify a failure-rate gate, validate a
nonce, or supply a scored result. No schedule or circuit parameter is selected
from those samples. A gate verdict is final under the repository rules.
