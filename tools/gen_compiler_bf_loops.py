#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler (Fix: Flattened Logic & Safe Data Handling)

import sys

S = " "
F = "\u3000"

def emit(s): sys.stdout.write(s + "\n")
def right(n=1): emit((S+S+S)*n)
def left(n=1): emit((S+S+F)*n)
def inc(n=1): emit((S+F+S)*n)
def dec(n=1): emit((S+F+F)*n)
def out(): emit(F+S+S)
def inp(): emit(F+S+F)
def loop_open(): emit(F+F+S)
def loop_close(): emit(F+F+F)
def clear(): loop_open(); dec(); loop_close()

# Memory Layout
# C98: Wall (0)
# C100+: Buffer [Flag, Data]
# Flag: 1=Filled, 2=Cursor

WALL_POS = 98
BUFFER_BASE = 100

def emit_bytes(vals):
    for v in vals:
        right(8); clear()
        if v > 0: inc(v)
        out(); clear(); left(8)
        right(7); inc(); left(7)

def stream_bytes(vals):
    first = True
    for v in vals:
        if not first:
            right(2)
        clear(); inc()
        right(1); clear()
        if v > 0: inc(v)
        left(1)
        first = False
    right(2); clear(); inc(2)

def go_home_from_cursor():
    left(2); loop_open(); left(2); loop_close(); left(WALL_POS)

def return_to_cursor_simple():
    right(WALL_POS); loop_open(); right(2); loop_close(); left(2)

def sub_and_check(delta, action_func):
    right(1); dec(delta)
    # Copy Data(R1) to Temp(R2) non-destructively
    loop_open(); left(1); inc(); right(2); inc(); left(1); dec(); loop_close()
    right(1); loop_open(); left(1); inc(); right(1); dec(); loop_close(); left(1)
    
    # Check Temp(R2)
    right(2); clear(); inc(); left(1) # Flag=1
    loop_open(); right(1); dec(); left(1); clear(); loop_close() # If R2!=0, Flag=0
    
    # If Flag=1 (Match), Execute
    right(1)
    loop_open()
    dec(); left(3); action_func(); right(3); clear()
    loop_close()
    left(3)

def pad_zeros(count):
    right(1); clear(); inc(count // 10)
    loop_open(); dec(); left(1)
    for _ in range(10):
        right(8); clear(); out(); clear(); left(8)
        right(7); inc(); left(7)
    right(1); loop_close(); left(1)

def main():
    target_file_size = 500
    load_addr = 0x400000
    header_len = 120
    def p64(v): return list(v.to_bytes(8, "little"))
    def p32(v): return list(v.to_bytes(4, "little"))
    header = [
        0x7f,0x45,0x4c,0x46,0x02,0x01,0x01,0x00,0,0,0,0,0,0,0,0,
        0x02,0x00,0x3e,0x00,0x01,0x00,0x00,0x00,
        *p64(load_addr + header_len), *p64(64), *p64(0), *p32(0),
        0x40,0x00,0x38,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    ]
    prog_header = [
        0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(target_file_size), *p64(0x10000), *p64(0x1000)
    ]
    
    emit_bytes(header + prog_header)
    right(1000)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    right(WALL_POS); clear(); left(WALL_POS)
    right(BUFFER_BASE); clear(); inc(2); left(BUFFER_BASE)
    
    # Outer Loop Setup
    left(BUFFER_BASE); right(90); inc(); loop_open()
    
    # Navigation
    right(10)
    return_to_cursor_simple()
    
    # Read Input
    right(1); inp()
    
    # --- Safe EOF Check ---
    # Data is at R1. Move R1 -> L1, L2.
    loop_open(); left(1); inc(); left(1); inc(); right(2); dec(); loop_close()
    
    # Check L1 (Destructive). Result in L3 (Flag).
    left(1); clear(); inc(); left(1) # L3=1
    loop_open(); right(1); dec(); left(1); clear(); loop_close() # If L2(was L1)!=0, L3=0.
    
    # If L3=1 (EOF), Flush & Exit
    left(1)
    loop_open()
    # Go Home & Flush
    left(1); loop_open(); left(2); loop_close(); left(WALL_POS)
    right(BUFFER_BASE)
    loop_open(); right(1); out(); right(1); loop_close()
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    pad_zeros(500)
    # Kill Loops
    left(BUFFER_BASE); right(90); dec(); left(90); right(BUFFER_BASE)
    left(2); dec(); right(2)
    loop_close()
    
    # Restore Data from L2 -> R1
    right(1) # At L2
    loop_open(); right(2); inc(); left(2); dec(); loop_close()
    right(2) # Back to Data(R1)
    
    # --- Process Char (Dense Switch) ---
    loop_open()
    sub_and_check(43, lambda: stream_bytes([0xfe, 0x03]))
    sub_and_check(1, lambda: stream_bytes([0xb8, 0x00, 0x00, 0x00, 0x00, 0xbf, 0x00, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]))
    sub_and_check(1, lambda: stream_bytes([0xfe, 0x0b]))
    sub_and_check(1, lambda: stream_bytes([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]))
    sub_and_check(14, lambda: stream_bytes([0x48, 0xff, 0xcb]))
    sub_and_check(2, lambda: stream_bytes([0x48, 0xff, 0xc3]))
    right(1); dec(29); left(1) # Skip [
    right(1); dec(2); left(1) # Skip ]
    clear()
    loop_close()
    
    go_home_from_cursor()
    left(10)
    loop_close()

if __name__ == "__main__":
    main()
