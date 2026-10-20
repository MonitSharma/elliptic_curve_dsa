# Fixed stronger late comparison at Q1264

Raw1264 is faster than the public Toffoli parent but the predeclared512-batch
development diagnostic has49 wrong-value shots versus16 in the parent. It is
not qualified. Textual source comparison finds the parent late chunk-compare
offset -4 versus this lineage's -5; other source/width differences remain.

Test one fixed stronger variant: global/hard1264, late comparison offset-3
(two more bits), all other shape bands and profiles unchanged. This increases
comparison precision. It does not remove gates or weaken correctness for a
packet. No official-packet input is used. It is not guaranteed to eliminate
errors or preserve a resource gain. Freeze source before generation; baseline
must reproduce7fe2bb94. Metadata-only replay traces must report the actual
predicate changes and preserve every capacity failure. Compare only the finished
variant on a new predeclared development label, then the final statistical gate
only if it is both competitive and plausibly admissible. No final gate or nonce
is declared or run by this generation experiment.
