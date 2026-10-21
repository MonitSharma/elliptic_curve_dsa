# Driver amendments before the final circuit or gate exists

19 October 2026. While only cache generation was running, `gate84.py` gained
source-manifest checks before and after the census and a separate resource
readiness check: paired mean saving minus two standard errors must be at
least 12 Toffolis to mark the circuit ready for nonce research. This does not
change the four failure-rate rules or turn a passed failure gate into a failed
one; insufficient resource margin gets its own status file. No census has run
for the final candidate and no final source has been frozen at amendment time.

The declaration records the actual gate driver SHA-256 at execution. The
original launch hash file is preserved, and `gate84-final-driver.sha256`
records the amended driver. The fixed 84-stage circuit generation schedule
and final census label/batch count are unchanged.
