# Attempt history

The first launcher, PID 658697, stopped with exit 1 at the resource admission
check before compiling or running source. Its snapshot counted transient
thread totals, including idle managers; the threshold could fluctuate as the
nonce workers created and destroyed helper threads between windows.

The revised admission reserves the search's worst-case 60 worker slots
(56 computation threads plus four waiting main threads), identifies only
recorded idle managers/ancestors, rejects other active research jobs, and uses
one build job. Memory and node load are checked again. The v2 build was
PID 665460.

Review of the protected simulator found that **both R and Hmr draw RNG even
behind false guards**. The v2 proof constrained only Hmr ordering and was
incomplete. Its build was stopped before any reordered stream existed;
STOP-V2.json preserves the verified PID, command and reason. Its actual logs,
exit marker and original source are retained. No resource result is accepted
from v2.

The corrected v3 run is PID 674779. The scheduler chains every R/Hmr event;
the coloring pass retains zero resets, inactive measurements and all Toffolis.
Ten scheduling controls pass, including reset/Hmr ordering, phase conflicts,
classical dependencies, missing/duplicate indices and 100 random unitary
networks checked on all 16 basis states. Existing recoloring controls include
new zero-reset and false-guard RNG-event checks. The full source screen and
width measurement remain pending. The actual v3 launcher is separately bound
in LAUNCH-V3-SOURCE.sha256; SOURCE-v3.sha256 also retains its v2 template hash.

The frozen parent4 search and its final verifier have not been changed.
