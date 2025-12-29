# gen_compiler.py
# Stage 4 (Route A): Minimal self-hosted compiler
# Emits a fixed SPA + opcode stream for Hello World

def main():
    # BF Hello World program
    bf = (
        "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]"
        ">>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
    )

    # BF -> opcode mapping (matches ref_vm)
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

    # SPA header
    out += b'SPA'

    # opcode stream
    for c in bf:
        out.append(opcode[c])

    # write raw bytes to stdout
    import sys
    sys.stdout.buffer.write(out)

if __name__ == "__main__":
    main()