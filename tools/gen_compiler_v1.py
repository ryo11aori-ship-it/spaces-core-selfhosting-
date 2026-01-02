#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Spaces Compiler Generator — robust variant with explicit loop balancing counters.
# - Emits a real '\n' after every logical emit to avoid accidental token merging.
# - Tracks loop_start/loop_end calls in Python (ls_count/le_count).
# - Appends missing loop_end tokens at EOF if ls_count > le_count.
#
# Save this as tools/gen_compiler_v1.py and run:
#   python3 tools/gen_compiler_v1.py > spaces/self/compiler_v1.spaces

import sys

def p64(val): return list(val.to_bytes(8, 'little'))
def p32(val): return list(val.to_bytes(4, 'little'))

S = " "         # half-width space
F = "\u3000"    # full-width space used by this esolang
CMDS = []

# loop counters (track how many explicit loop_start/loop_end we emitted)
ls_count = 0
le_count = 0

def emit(s):
    # Append a real newline after each logical emit to ensure no accidental merging
    # between adjacent emits (newlines are ignored by the VM).
    CMDS.append(s + '\n')

def right(n=1): emit((S+S+S)*n)
def left(n=1): emit((S+S+F)*n)
def inc(n=1): emit((S+F+S)*n)
def dec(n=1): emit((S+F+F)*n)
def out(): emit(F+S+S)
def inp(): emit(F+S+F)

def loop_start():
    global ls_count
    ls_count += 1
    emit(F+F+S)

def loop_end():
    global le_count
    le_count += 1
    emit(F+F+F)

def clear(): 
    # clear current cell: [ loop_start(); dec(); loop_end() ]
    # keep using loop_start()/loop_end() so python counters remain accurate.
    loop_start()
    dec()
    loop_end()

# --- Tracked byte-emission helpers ---
# Uses C0 -> C9 trick for output then increments C7 counter.
def emit_byte_tracked(val):
    # Output byte (C0 -> C9 -> C0)
    right(9); clear(); inc(val); out(); clear(); left(9)
    # Increment Counter C7 (C0 -> C7 -> C0)
    right(7); inc(); left(7)

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list:
        emit_byte_tracked(b)

def main():
    # Safety margin
    right(16)

    # 1. ELF header (minimal, target total_size 200)
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
    for b in header + prog_header:
        emit_byte_tracked(b)

    # 2. xor rbx, rbx
    emit_machine_code_tracked([0x48, 0x31, 0xdb])

    # 3. Main Loop
    # C2 is main loop flag
    right(2); clear(); inc(); loop_start(); left(2)

    # [STEP1] read input into C0
    clear()
    inp()

    # [STEP2] EOF check: copy C0 -> C1 & C3; check preserved copy in C1
    right(); clear(); left()            # clear C1

    # copy C0 -> C1 & C3 (transient)
    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # assume EOF: C5 = 1
    right(5); clear(); inc(); left(5)

    # if C1 != 0 then clear C5
    right(1); loop_start(); clear(); right(4); clear(); left(4); loop_end(); left(1)

    # if C5==1 break main loop C2
    right(5)
    loop_start()
    clear()           # clear flag to avoid loop forever
    left(3); dec(); right(3)
    loop_end()
    left(5)

    # [STEP3] check '+'
    right(2); loop_start(); left(2)

    right(); clear(); left()

    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # subtract 43 from preserved C1
    right(1); dec(43); left(1)

    # check C1 == 0 -> set C5 = 1 if match
    right(5); clear(); inc(); left(5)
    right(1); loop_start(); clear(); right(4); clear(); left(4); loop_end(); left(1)

    # if match emit inc rbx machine code
    right(5); loop_start()
    clear()
    left(5)
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3)
    right(5)
    loop_end(); left(5)

    right(2); loop_end(); left(2)

    # [STEP4] check '-'
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

    # 4. exit sequence
    emit_machine_code_tracked([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 5. pad to 200 bytes
    right(7); dec(200); loop_start(); inc(200); left(7); emit_byte_tracked(0); right(7); dec(200); loop_end(); inc(200); left(7)

    # --- Post-process: append missing loop_end tokens exactly as counted ---
    out_str = "".join(CMDS)
    # Python-side counters ls_count / le_count were updated by loop_start()/loop_end() calls
    global ls_count, le_count
    # Note: variables are defined at module top; ensure we reference them.
    try:
        ls = ls_count
        le = le_count
    except NameError:
        # fallback when executed in different context
        ls = out_str.count(F+F+S + '\n')
        le = out_str.count(F+F+F + '\n')

    if ls > le:
        missing = ls - le
        # append exactly `missing` loop_end tokens (without newline merging risk)
        out_str += (F + F + F + '\n') * missing

    # Final write
    sys.stdout.buffer.write(out_str.encode('utf-8'))

if __name__ == '__main__':
    main()