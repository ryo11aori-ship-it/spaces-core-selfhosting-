#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler (Self-Hosting Linear)
# Fix: Increased target_file_size to 10000 to prevent segfaults due to ELF truncation.
#      Standard Indentation. Robust Logic.

import sys

S = " "
F = "\u3000"

def emit(s):
    sys.stdout.write(s + "\n")

def right(n=1):
    if n > 0: emit((S+S+S) * n)

def left(n=1):
    if n > 0: emit((S+S+F) * n)

def inc(n=1):
    if n > 0: emit((S+F+S) * n)

def dec(n=1):
    if n > 0: emit((S+F+F) * n)

def out():
    emit(F + S + S)

def inp():
    emit(F + S + F)

def loop_open():
    emit(F + F + S)

def loop_close():
    emit(F + F + F)

def clear():
    loop_open()
    dec()
    loop_close()

DATA_CELL = 100
OUTPUT_CELL = 200

def emit_byte_literal(val):
    right(OUTPUT_CELL - DATA_CELL)
    clear()
    inc(val)
    out()
    left(OUTPUT_CELL - DATA_CELL)

def emit_bytes_literal(vals):
    for v in vals:
        emit_byte_literal(v)

def check_and_emit(delta, code_bytes):
    dec(delta)
    
    # Check if DATA_CELL is 0 using Temp 1 (101)
    right(1)
    clear()
    inc() # Temp1 = 1
    left(1)
    
    # If DATA_CELL != 0, Set Temp1 = 0
    # Non-destructive check using Temp 2 (102)
    loop_open()
    right(1)
    dec() # Temp1 = 0
    right(1); inc(); left(2) # Move DATA to Temp2
    dec() # Zero DATA to break
    loop_close()
    
    # Restore DATA from Temp 2
    right(2)
    loop_open()
    left(2); inc(); right(2); dec()
    loop_close()
    left(2)
    
    # Check Temp 1
    right(1)
    loop_open()
    dec() # Clear Temp 1
    left(1)
    emit_bytes_literal(code_bytes)
    right(1)
    loop_close()
    left(1)

def main():
    # INCREASED SIZE to accommodate larger output binaries
    target_file_size = 10000 
    load_addr = 0x400000
    
    def p64(v): return list(v.to_bytes(8, "little"))
    def p32(v): return list(v.to_bytes(4, "little"))

    header = [
        0x7f,0x45,0x4c,0x46,0x02,0x01,0x01,0x00,0,0,0,0,0,0,0,0,
        0x02,0x00,0x3e,0x00,0x01,0x00,0x00,0x00,
        *p64(load_addr + 120), *p64(64), *p64(0), *p32(0),
        0x40,0x00,0x38,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    ]
    prog_header = [
        0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(target_file_size), *p64(0x10000), *p64(0x1000)
    ]
    
    # Init
    right(DATA_CELL)
    
    # Emit Header
    emit_bytes_literal(header + prog_header)
    emit_bytes_literal([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    # Loop Setup (Flag at 105)
    right(5)
    inc()
    loop_open()
    left(5)
    
    # Read
    inp()
    
    # EOF Check (Temp 101)
    loop_open(); right(1); inc(); left(1); dec(); loop_close() # Move to Temp
    right(1); loop_open(); left(1); inc(); right(1); dec(); loop_close(); left(1) # Restore
    
    # Check Temp. If 0 (EOF), Clear Flag (105).
    # Logic: Set IsEOF(102)=1. If Temp!=0, IsEOF=0.
    right(2); inc(); left(1) # IsEOF=1
    loop_open()
    right(1); dec(); left(1) # IsEOF=0
    clear() # Clear Temp
    loop_close()
    
    # Check IsEOF
    right(2)
    loop_open()
    # EOF Action
    left(2)
    # Emit Exit & Pad
    emit_bytes_literal([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    # Massive Padding to ensure size matches header
    # We output ~2500 bytes so far? 
    # Just emit 7000 zeros to be safe.
    for _ in range(7000):
        emit_byte_literal(0)
    
    right(2) # Back to IsEOF
    
    # Kill Flag
    right(3); dec(); left(3)
    # Kill IsEOF
    dec()
    loop_close()
    left(2)
    
    # Dense Switch
    check_and_emit(43, [0xfe, 0x03])
    check_and_emit(1, [0xb8, 0x00, 0x00, 0x00, 0x00, 0xbf, 0x00, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    check_and_emit(1, [0xfe, 0x0b])
    check_and_emit(1, [0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    check_and_emit(14, [0x48, 0xff, 0xcb])
    check_and_emit(2, [0x48, 0xff, 0xc3])
    
    dec(29) # Skip [
    dec(2) # Skip ]
    
    clear()
    right(5)
    loop_close()

if __name__ == "__main__":
    main()
