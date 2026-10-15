import unittest
from analyze import analyze, magnitude_info, representable, P


def log(family="a", events=(), bad=False):
    b = str(bad).lower()
    return (f"TRACE family={family} shot=0 final_bad={b} x_bad={b} y_bad=false events={len(events)}\n"
            + "\n".join(f"  EVENT family={family} shot=0 {e}" for e in events)
            + f"\nTRACE_SUMMARY family={family} shots=1 observer_equal=true score=NONE\n")


MARK = "TRACE_MARKS total=4 by_kind={} last_tick={}\n"
EVENT = "at=7 FWD_RAIL phase=divide tick=2 corrupt=source widths=[5, 5] tape=[0, 0, 0, 0, 0] diff_t=0x0"


class AuditTests(unittest.TestCase):
    def test_signed_range(self):
        for n in range(-35, 36):
            self.assertEqual(representable(n % P, 5, False), -16 <= n <= 15)

    def test_parked_low_range_and_parity(self):
        for n in range(-35, 36):
            self.assertEqual(representable(n % P, 5, True), -31 <= n <= 31 and n % 2 == 1)

    def test_full_width_multiple_lifts(self):
        for n in (0, 1, 2, P // 2, P - 1):
            self.assertTrue(representable(n, 257, False))
            self.assertTrue(representable(n, 257, True))

    def test_zero_is_not_power_of_two(self):
        self.assertFalse(magnitude_info(0, 5)["target_nonzero_power_of_two"])

    def test_positive_and_negative_powers(self):
        for diff in (32, P - 32):
            self.assertEqual(magnitude_info(diff, 5)["target_exponent_minus_width"], 0)

    def test_nonpower(self):
        self.assertIsNone(magnitude_info(12, 5)["target_exponent"])

    def test_families_do_not_mix(self):
        r = analyze(MARK + log("a", [EVENT], True) + log("b"))["families"]
        self.assertEqual(r["a"]["forward_events"], 1)
        self.assertEqual(r["b"]["first_kind"], {"NO_OBSERVED_EVENT": 1})

    def test_missing_summary(self):
        with self.assertRaises(ValueError):
            analyze(MARK + log().split("TRACE_SUMMARY")[0])

    def test_missing_shot(self):
        with self.assertRaises(ValueError):
            analyze(MARK + log().replace("shots=1", "shots=2"))

    def test_event_count(self):
        with self.assertRaises(ValueError):
            analyze(MARK + log("a", [EVENT]).replace("events=1", "events=2"))

    def test_duplicate(self):
        with self.assertRaises(ValueError):
            analyze(MARK + log() + log())

    def test_malformed(self):
        with self.assertRaises(ValueError):
            analyze(MARK + log().replace("final_bad=false", "final_bad=unknown"))

    def test_order(self):
        ev = [EVENT.replace("at=7", "at=10"), EVENT]
        result = analyze(MARK + log("a", ev))
        self.assertEqual(result["families"]["a"]["shots_detail"][0]["first"]["at"], 7)


if __name__ == "__main__":
    unittest.main()
