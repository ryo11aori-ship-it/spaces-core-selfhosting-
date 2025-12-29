#!/usr/bin/env python3
# gen_compiler.py
# Self-hosted BF -> SPA binary compiler
# Reads BF source from stdin, writes SPA binary to stdout

import sys

OPCODE = {
    '>': 0x01,
    '<': 0x02,
    '+': 0x03,
    '-': 0x04,
    '.': 0x05,
    ',': 0x06,
    '[': 0x07,
    ']': 0x08,
}

def main():
    data = sys.stdin.read()
    out = bytearray()

    # SPA header
    out += b'SPA'

    for c in data:
        if c in OPCODE:
            out.append(OPCODE[c])

    sys.stdout.buffer.write(out)

if __name__ == "__main__":
    main()