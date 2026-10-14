"""Exercise clean-boundary assumptions and malformed-frame rejection."""
import ctypes
import ctypes.util
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("lifetime", Path(__file__).with_name("analyze-wire-lifetimes.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        library = ctypes.util.find_library("zstd")
        if not library:
            raise unittest.SkipTest("Requires system libzstd (available on research server)")
        cls.lib = ctypes.CDLL(library)
        cls.lib.ZSTD_compressBound.argtypes = [ctypes.c_size_t]
        cls.lib.ZSTD_compressBound.restype = ctypes.c_size_t
        cls.lib.ZSTD_compress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
        cls.lib.ZSTD_compress.restype = ctypes.c_size_t
        cls.lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
        cls.lib.ZSTD_isError.restype = ctypes.c_uint

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ops.bin"

    def row(self, kind, target=MODULE.NO, condition=MODULE.NO, c1=MODULE.NO):
        return MODULE.ROW.pack(kind, 0, MODULE.NO, c1, target, MODULE.NO, condition, MODULE.NO)

    def write(self, rows, count=None):
        data = b"".join(rows)
        raw = ctypes.create_string_buffer(data)
        capacity = self.lib.ZSTD_compressBound(len(data))
        compressed = ctypes.create_string_buffer(capacity)
        size = self.lib.ZSTD_compress(compressed, capacity, raw, len(data), 3)
        self.assertFalse(self.lib.ZSTD_isError(size))
        header = b"QECCOPSZ" + struct.pack("<Q", len(rows) if count is None else count)
        self.path.write_bytes(header + compressed.raw[:size])

    def test_unconditional_reset_permits_disjoint_intervals(self):
        self.write([self.row(2, 0), self.row(8, 2, c1=0), self.row(11, 2),
                    self.row(8, 1, c1=0), self.row(11, 1)])
        report = MODULE.analyze(self.path)
        self.assertEqual(report["physical_width"], 3)
        self.assertEqual(report["conservative_peak_live_intervals"], 2)
        self.assertEqual(report["fixed_abi_qubits"], 1)

    def test_conditional_reset_does_not_free_a_dirty_passenger(self):
        self.write([self.row(2, 0), self.row(8, 2, c1=0), self.row(15, condition=0),
                    self.row(11, 2), self.row(16), self.row(8, 1, c1=0), self.row(11, 1)])
        report = MODULE.analyze(self.path)
        self.assertEqual(report["conservative_peak_live_intervals"], 3)
        self.assertEqual(report["unsplit_conditional_resets"], 1)

    def test_abi_qubits_stay_reserved_after_reset(self):
        self.write([self.row(2, 0), self.row(2, 2), self.row(11, 2),
                    self.row(8, 1, c1=0), self.row(11, 1)])
        self.assertEqual(MODULE.analyze(self.path)["conservative_peak_live_intervals"], 3)

    def test_truncated_counts_and_unbalanced_conditions_reject(self):
        self.write([self.row(6, 0)], count=2)
        with self.assertRaises(ValueError):
            MODULE.analyze(self.path)
        self.write([self.row(16)])
        with self.assertRaises(ValueError):
            MODULE.analyze(self.path)


if __name__ == "__main__":
    unittest.main()
