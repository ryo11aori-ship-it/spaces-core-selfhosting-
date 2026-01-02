#!/usr/bin/env python3
# tools/gen_compiler_bf_full.py
# Level 1.7: Full Brainfuck Compiler (Buffered I/O with Token Strategy)
# Fixed: Completely removed indentation to prevent Syntax Errors.

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

# --- Memory Layout ---
# C0: Input Char
# C1-C6: Scratch
# C7: Output Byte Counter
# C8: Output Buffer Count (Current Size)
# C100+: Code Buffer
# C300+: Append Token Track (Tracks End of Buffer)
# C500+: Read Token Track (Tracks Current Read Pos)

BUFFER_BASE = 100
APPEND_TOKEN_BASE = 300
READ_TOKEN_BASE = 500

def emit_byte_tracked(val):
    right(8); clear()
    if val > 0: inc(val)
    out(); clear(); left(8)
    right(7); inc(); left(7)

def emit_bytes(vals):
    for v in vals: emit_byte_tracked(v)

def copy_c0_to_c1():
    right(1); clear(); right(2); clear(); left(3)
    loop_open(); dec(); right(1); inc(); right(2); inc(); left(3); loop_close()
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(3)

# バッファ書き込み (Append)
# C300にあるトークン(255)を探し、その位置に対応するC100番地に書き込み、トークンを右にずらす
def append_safe(vals):
    for v in vals:
        # Go to Append Token Base
        right(APPEND_TOKEN_BASE)
        # Scan Right for Token (255)
        loop_open(); right(); loop_close()
        # Now at C300 + Offset. Move to C100 + Offset (Left 200)
        left(200)
        # Write Value
        clear()
        if v > 0: inc(v)
        # Back to Token (Right 200)
        right(200)
        # Move Token Right [->+<]
        loop_open(); dec(); right(); inc(); left(); loop_close()
        # Scan Left to Wall (C299)
        loop_open(); left(); loop_close()
        # Back to C0
        left(APPEND_TOKEN_BASE - 1)
        # Increment Count C8
        right(8); inc(); left(8)

def check_char(char_code, logic_func):
    copy_c0_to_c1()
    right(1); dec(char_code)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(3); logic_func(); right(3); clear(); loop_close(); left(3)

def main():
    total_size = 1000
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
        *p64(total_size), 
        *p64(0x10000), 
        *p64(0x1000)
    ]
    
    emit_bytes(header + prog_header)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])

    # Init Wall and Token for Append (C299=Wall, C300=Token)
    right(APPEND_TOKEN_BASE - 1); inc(255); right(); inc(255); left(APPEND_TOKEN_BASE)

    # Init Wall and Token for Read (C499=Wall, C500=Token)
    right(READ_TOKEN_BASE - 1); inc(255); right(); inc(255); left(READ_TOKEN_BASE)

    # Main Loop
    right(2); clear(); inc(); left(2)
    right(2); loop_open(); left(2)
    
    clear(); inp()
    
    # EOF Check
    copy_c0_to_c1()
    right(3); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(1); clear(); right(1); clear(); loop_close(); left(3)
    
    # Checks
    check_char(62, lambda: append_safe([0x48, 0xff, 0xc3]))
    check_char(60, lambda: append_safe([0x48, 0xff, 0xcb]))
    check_char(43, lambda: append_safe([0xfe, 0x03]))
    check_char(45, lambda: append_safe([0xfe, 0x0b]))
    
    check_char(46, lambda: append_safe([
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x48, 0x89, 0xde,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]))
    
    check_char(44, lambda: append_safe([
        0xb8, 0x00, 0x00, 0x00, 0x00,
        0xbf, 0x00, 0x00, 0x00, 0x00,
        0x48, 0x89, 0xde,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]))
    
    right(2); loop_close(); left(2)
    
    # Flush Buffer
    # Loop C8 times
    right(8)
    loop_open()
    dec(); left(8)
    # Go to Read Token Base
    right(READ_TOKEN_BASE)
    # Scan Right for Token
    loop_open(); right(); loop_close()
    # Now at C500 + Offset. Move to C100 + Offset (Left 400)
    left(400)
    # Output Byte
    out()
    # Back to Token (Right 400)
    right(400)
    # Move Token Right
    loop_open(); dec(); right(); inc(); left(); loop_close()
    # Scan Left to Wall (C499)
    loop_open(); left(); loop_close()
    # Back to C0
    left(READ_TOKEN_BASE - 1)
    # Loop end C8
    right(8)
    loop_close()
    left(8)

    # Exit
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    
    # Padding
    right(7); dec(total_size)
    left(1); dec(total_size)
    loop_open()
    inc(total_size)
    right(1); clear(); out(); left(1)
    dec(total_size)
    loop_close()

if __name__ == "__main__":
    main()
