#!/usr/bin/env python3
# gen_compiler.py (Route A)
# Produce a raw binary: header "SPA" then opcode bytes (1..8) for a fixed Hello World BF program.

import sys

def main():
    bf = (
        "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]"
        ">>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
    )

    opcode = {
        '>': 0x01,
        '<': 0x02,
        '+': 0x03,
        '-': 0x04,
        '.': 0x05,
        ',': 0x06,
        '[': 0x07,
        ']': 0x08,
    }

    out = bytearray()
    out += b'SPA'
    for c in bf:
        if c not in opcode:
            # skip any unexpected char (safety)
            continue
        out.append(opcode[c])

    sys.stdout.buffer.write(out)

if __name__ == "__main__":
    main()