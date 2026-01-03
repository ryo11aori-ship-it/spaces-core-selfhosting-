#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler (Optimization: Source Code Size Reduction)
# Fix: Replaced unrolled padding with runtime BF loops.
#      Optimized byte streaming to minimize tape movement.

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

# Optimized Emitter: Moves to Output, writes ALL bytes, then returns.
# Drastically reduces source code size compared to per-byte movement.
def emit_bytes_literal(vals):
    if not vals: return
    
    # Move to OUTPUT_CELL
    right(OUTPUT_CELL - DATA_CELL)
    
    for v in vals:
        clear()
        if v > 0: inc(v)
        out()
    
    # Return to DATA_CELL
    left(OUTPUT_CELL - DATA_CELL)

# Runtime Padding: Generates a BF loop to output zeros.
# Prevents "File too large" errors by not unrolling loops in source code.
def emit_padding_loop(count):
    # We need to output 'count' zeros.
    # We use OUTPUT_CELL+1 as the counter.
    # 1. Move to Counter (OUTPUT_CELL+1)
    right(OUTPUT_CELL - DATA_CELL + 1)
    clear()
    
    # We can't set huge numbers easily with simple inc.
    # We use nested loops for large counts.
    # count = outer * inner + remainder
    outer = count // 100
    remainder = count % 100
    
    if outer > 0:
        inc(outer)
        loop_open() # Outer Loop
        # Set Inner Counter (OUTPUT_CELL+2) to 100
        right(1); clear(); inc(100)
        loop_open() # Inner Loop
        # Output 0 at OUTPUT_CELL
        left(2) # Go to OUTPUT_CELL
        clear(); out()
        right(2) # Back to Inner Counter
        dec()
        loop_close() # End Inner
        
        left(1) # Back to Outer Counter
        dec()
        loop_close() # End Outer
        
    if remainder > 0:
        # Simple remaining loop
        inc(remainder)
        loop_open()
        left(1) # Go to OUTPUT_CELL
        clear(); out()
        right(1) # Back to Counter
        dec()
        loop_close()

    # Return to DATA_CELL
    left(OUTPUT_CELL - DATA_CELL + 1)

def check_and_emit(delta, code_bytes):
    dec(delta)
    
    # Check if DATA_CELL is 0 using Temp 1 (101)
    right(1)
    clear()
    inc() # Temp1 = 1
    left(1)
    
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
    # Target large enough for self-hosted compiler
    target_file_size = 12000
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
    
    # Emit Header (Batch optimized)
    emit_bytes_literal(header + prog_header)
    emit_bytes_literal([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    # Keep track of emitted size to calculate padding
    emitted_size = len(header) + len(prog_header) + 7
    # + EOF Exit Code size (10 bytes)
    padding_size = target_file_size - emitted_size - 10
    
    # Loop Setup (Flag at 105)
    right(5)
    inc()
    loop_open()
    left(5)
    
    # Read
    inp()
    
    # EOF Check logic (same as before)
    loop_open(); right(1); inc(); left(1); dec(); loop_close()
    right(1); loop_open(); left(1); inc(); right(1); dec(); loop_close(); left(1)
    
    right(2); inc(); left(1)
    loop_open()
    right(1); dec(); left(1)
    clear()
    loop_close()
    
    # Check IsEOF (102)
    right(2)
    loop_open()
    # EOF Action
    left(2)
    emit_bytes_literal([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    
    # Efficient Runtime Padding
    emit_padding_loop(padding_size)
    
    right(2) # Back to IsEOF
    
    # Kill Flags
    right(3); dec(); left(3)
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
    
    dec(29)
    dec(2)
    
    clear()
    right(5)
    loop_close()

if __name__ == "__main__":
    main()
