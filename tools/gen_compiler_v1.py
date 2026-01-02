#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Robust Spaces generator — guarantees balanced loop tokens by Python-side counting.
#
# Usage:
#   python3 tools/gen_compiler_v1.py > spaces/self/compiler_v1.spaces
#
# After generation, verify:
#   python3 - <<'PY'
#   s = open('spaces/self/compiler_v1.spaces','r',encoding='utf-8').read()
#   print("LS", s.count('\u3000\u3000 '), "LE", s.count('\u3000\u3000\u3000'))
#   PY
#
# Then run your VM exactly as in CI.

import sys

def p64(val): return list(val.to_bytes(8, 'little'))
def p32(val): return list(val.to_bytes(4, 'little'))

# Symbols used by the esolang / vm
S = " "         # ASCII half-width space
F = "\u3000"    # full-width space (U+3000)

# We'll collect "chunks" and then join once at the end.
CHUNKS = []

# Python-side counters for loop tokens we intentionally emit
LS_COUNT = 0
LE_COUNT = 0

def emit(s):
    # Append a real newline between emitted logical chunks to avoid accidental boundary merging.
    # The VM ignores newline characters, so these are safe separators.
    CHUNKS.append(s + '\n')

def right(n=1): emit((S+S+S)*n)
def left(n=1): emit((S+S+F)*n)
def inc(n=1): emit((S+F+S)*n)
def dec(n=1): emit((S+F+F)*n)
def out(): emit(F+S+S)
def inp(): emit(F+S+F)

def loop_start():
    global LS_COUNT
    LS_COUNT += 1
    emit(F+F+S)

def loop_end():
    global LE_COUNT
    LE_COUNT += 1
    emit(F+F+F)

def clear():
    # clear cell: loop_start(); dec(); loop_end()
    loop_start()
    dec()
    loop_end()

# helpers to emit machine bytes while tracking output-counter C7
def emit_byte_tracked(val):
    # pattern: move to C9, clear, inc(val), out, clear, move back
    right(9); clear(); inc(val); out(); clear(); left(9)
    # increment byte counter C7
    right(7); inc(); left(7)

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list:
        emit_byte_tracked(b)

def main():
    # Safety margin
    right(16)

    # 1) ELF headers (target total size 200)
    load_addr = 0x400000
    header_len = 120
    total_size = 200

    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        *p64(load_addr + header_len), *p64(64), *p64(0), *p32(0),
        0x40, 0x00, 0x38, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    prog_header = [
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(total_size), *p64(total_size), *p64(0x1000)
    ]
    for b in (header + prog_header):
        emit_byte_tracked(b)

    # 2) init code xor rbx, rbx
    emit_machine_code_tracked([0x48, 0x31, 0xdb])

    # 3) Main loop start (C2 = 1)
    right(2); clear(); inc(); loop_start(); left(2)

    # STEP 1: read input (into C0)
    clear()
    inp()

    # STEP 2: EOF check
    # Clear C1
    right(); clear(); left()

    # Copy C0 -> C1 & C3 (transient via loops)
    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # Assume EOF: C5 = 1
    right(5); clear(); inc(); left(5)

    # If C1 != 0, clear C5 (so it's not EOF)
    right(1); loop_start(); clear(); right(4); clear(); left(4); loop_end(); left(1)

    # If C5 == 1 then break main loop (dec C2)
    right(5)
    loop_start()
    clear()            # clear the flag to avoid infinite re-break
    left(3); dec(); right(3)
    loop_end()
    left(5)

    # STEP 3: check '+'
    right(2); loop_start(); left(2)

    right(); clear(); left()

    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # Subtract 43 from preserved C1
    right(1); dec(43); left(1)

    # If C1 == 0 set match flag C5=1
    right(5); clear(); inc(); left(5)
    right(1); loop_start(); clear(); right(4); clear(); left(4); loop_end(); left(1)

    # If match emit inc rbx
    right(5); loop_start()
    clear()
    left(5)
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3)
    right(5)
    loop_end(); left(5)

    right(2); loop_end(); left(2)

    # STEP 4: check '-'
    right(2); loop_start(); left(2)

    right(); clear(); left()

    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    right(1); dec(45); left(1)

    right(5); clear(); inc(); left(5)
    right(1); loop_start(); clear(); right(4); clear(); left(4); loop_end(); left(1)

    right(5); loop_start()
    clear()
    left(5)
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xcb)
    right(5)
    loop_end(); left(5)

    right(2); loop_end(); left(2)

    right(2); loop_end(); left(2)

    # 4) exit sequence (mov edi, ebx; mov eax,60; syscall)
    emit_machine_code_tracked([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 5) pad to total size (emit zeros)
    right(7); dec(200); loop_start(); inc(200); left(7); emit_byte_tracked(0); right(7); dec(200); loop_end(); inc(200); left(7)

    # --- Post-process: balance loop tokens if necessary ---
    out_str = "".join(CHUNKS)

    # Count plain patterns (without assuming newlines)
    loop_start_pat = F + F + S
    loop_end_pat = F + F + F

    ls = out_str.count(loop_start_pat)
    le = out_str.count(loop_end_pat)

    if ls > le:
        missing = ls - le
        # Append missing loop_end tokens exactly to the string (no newline needed)
        out_str += (loop_end_pat) * missing

    # Final write
    sys.stdout.buffer.write(out_str.encode('utf-8'))

if __name__ == '__main__':
    main()