"""Conservative physical-wire intervals from an unchanged compressed stream.

Only unconditional R/Hmr creates a clean boundary. ABI qubits are reserved
throughout. An unfinished interval remains live to stream end, even if its last
touch was much earlier. This is an allocation analysis, never a qualified score.
Uses system libzstd, no new contestant dependency or harness change.
"""
import argparse
import ctypes
import ctypes.util
import hashlib
import heapq
import json
from pathlib import Path
import struct
import time

NO = (1 << 64) - 1
ROW = struct.Struct("<IIQQQQQQ")


class Buffer(ctypes.Structure):
    _fields_ = [("src", ctypes.c_void_p), ("size", ctypes.c_size_t), ("pos", ctypes.c_size_t)]


def records(path):
    library = ctypes.util.find_library("zstd")
    if library is None:
        raise RuntimeError("System libzstd unavailable; run this research tool on smu_server")
    lib = ctypes.CDLL(library)
    lib.ZSTD_createDStream.restype = ctypes.c_void_p
    lib.ZSTD_freeDStream.argtypes = [ctypes.c_void_p]
    lib.ZSTD_initDStream.argtypes = [ctypes.c_void_p]
    lib.ZSTD_initDStream.restype = ctypes.c_size_t
    lib.ZSTD_decompressStream.argtypes = [ctypes.c_void_p, ctypes.POINTER(Buffer), ctypes.POINTER(Buffer)]
    lib.ZSTD_decompressStream.restype = ctypes.c_size_t
    lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
    lib.ZSTD_isError.restype = ctypes.c_uint
    state = lib.ZSTD_createDStream()
    if not state:
        raise MemoryError("zstd stream allocation")
    try:
        if lib.ZSTD_isError(lib.ZSTD_initDStream(state)):
            raise ValueError("zstd initialization")
        with path.open("rb") as source:
            header = source.read(16)
            if len(header) != 16 or header[:8] != b"QECCOPSZ":
                raise ValueError("Bad stream header")
            count = struct.unpack_from("<Q", header, 8)[0]
            if count > 4_000_000_000:
                raise ValueError("Operation cap")
            remainder = b""
            emitted = 0
            output = ctypes.create_string_buffer(4 * 1024 * 1024)
            status = 1
            while block := source.read(1024 * 1024):
                storage = ctypes.create_string_buffer(block)
                input_buffer = Buffer(ctypes.cast(storage, ctypes.c_void_p), len(block), 0)
                while input_buffer.pos < input_buffer.size:
                    output_buffer = Buffer(ctypes.cast(output, ctypes.c_void_p), len(output), 0)
                    status = lib.ZSTD_decompressStream(state, ctypes.byref(output_buffer), ctypes.byref(input_buffer))
                    if lib.ZSTD_isError(status):
                        raise ValueError("Malformed compressed frame")
                    data = remainder + output.raw[:output_buffer.pos]
                    end = len(data) - len(data) % ROW.size
                    for row in ROW.iter_unpack(data[:end]):
                        emitted += 1
                        if emitted > count:
                            raise ValueError("Trailing decompressed operations")
                        yield emitted - 1, row
                    remainder = data[end:]
            if status != 0 or remainder or emitted != count:
                raise ValueError("Incomplete operation frame")
    finally:
        lib.ZSTD_freeDStream(state)


def analyze(path):
    began = time.monotonic()
    starts = {}
    locked = set()
    intervals = []
    depth = 0
    operations = 0
    ccx = ccz = boundaries = conditional_resets = 0
    max_physical = -1
    for index, row in records(path):
        kind, padding, c2, c1, target, bit, condition, register = row
        if kind > 17 or padding:
            raise ValueError(f"Invalid record at {index}")
        qubits = [q for q in (c2, c1, target) if q != NO]
        for q in qubits:
            max_physical = max(max_physical, q)
            if kind == 2:
                locked.add(q)
            starts.setdefault(q, index)
        if kind == 15:
            depth += 1
        elif kind == 16:
            depth -= 1
            if depth < 0:
                raise ValueError("Unbalanced condition stack")
        elif kind in (11, 12):
            if depth == 0 and condition == NO and target not in locked:
                intervals.append((starts.pop(target), index, target))
                boundaries += 1
            else:
                conditional_resets += 1
        ccx += kind == 13
        ccz += kind == 14
        operations = index + 1
    if depth:
        raise ValueError("Unclosed condition stack")
    # ABI reservation begins at zero even if annotations are delayed.
    intervals = [(start, end, q) for start, end, q in intervals if q not in locked]
    intervals.extend((0 if q in locked else start, operations, q) for q, start in starts.items())
    intervals.extend((0, operations, q) for q in locked if q not in starts)
    intervals.sort()
    live = []
    peak = 0
    first_peak = None
    for start, end, q in intervals:
        while live and live[0] < start:
            heapq.heappop(live)
        heapq.heappush(live, end)
        if len(live) > peak:
            peak = len(live)
            first_peak = start
    return {"status": "allocation_analysis_only", "source_stream": str(path.resolve()),
            "operations": operations, "physical_width": max_physical + 1,
            "fixed_abi_qubits": len(locked), "unconditional_clean_boundaries": boundaries,
            "unsplit_conditional_resets": conditional_resets,
            "intervals": len(intervals), "conservative_peak_live_intervals": peak,
            "first_peak_operation": first_peak, "emitted_ccx": ccx, "emitted_ccz": ccz,
            "elapsed_seconds": time.monotonic() - began,
            "qualification": "No candidate source or full benchmark; not a scored width reduction."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stream", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = analyze(args.stream)
    digest = hashlib.sha256()
    with args.stream.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    result["stream_sha256"] = digest.hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
