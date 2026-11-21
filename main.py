#!/usr/bin/env python3
"""main.py - make.fun entrypoint.

Validates the pre-rendered entry.png that ships in this repo (produced by
draw.py) and copies it into the output directory given by the
MAKEFUN_OUTPUT_DIR environment variable (default /output).

Validation: the file must be a PNG of exactly 1024x1024 pixels and at most
1 MiB. Standard library only.
"""
import os
import shutil
import struct
import sys

MAX_BYTES = 1024 * 1024  # 1 MiB
EXPECTED = (1024, 1024)


def png_size(path):
    """Return (width, height) read from the PNG IHDR chunk."""
    with open(path, "rb") as fh:
        head = fh.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    if head[12:16] != b"IHDR":
        raise ValueError("missing IHDR chunk")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("entry.png not found next to main.py", file=sys.stderr)
        return 1
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        print("entry.png is %d bytes, over the 1 MiB limit" % size,
              file=sys.stderr)
        return 1
    dims = png_size(src)
    if dims != EXPECTED:
        print("entry.png is %dx%d, expected %dx%d"
              % (dims + EXPECTED), file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("copied %s -> %s (%d bytes, %dx%d)"
          % (src, dst, size, dims[0], dims[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
