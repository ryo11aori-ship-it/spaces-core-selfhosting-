#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.8: Full Brainfuck Compiler with Loops
# Fix: Fixed navigation bug in patching logic.
#      Always return to Token Track before scanning left to Wall.

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
# C0: Input Char
# C1-C6: Scratch
# C7: Output Byte Counter
# C8: Output Buffer Count
# C40: Loop Start Index (Simple Stack for 1 level)
# C98: Buffer Wall (0)
# C99: Buffer Sentinel (255)
# C100+: Buffer [Flag, Data]
# C298: Token Wall (0)
# C300+: Token Track

WALL_POS = 98
BUFFER_BASE = 100
TOKEN_WALL_POS = 298
TOKEN_BASE = 300

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

def append_safe(vals):
    for v in vals:
        right(BUFFER_BASE)
        loop_open(); right(2); loop_close()
        inc()
        right(1); clear()
        if v > 0: inc(v)
        right(1); clear()
        left(2); loop_open(); left(2); loop_close()
        left(WALL_POS); right(8); inc(); left(8)

def compile_bracket_open():
    append_safe([0x80, 0x3b, 0x00])
    append_safe([0x74, 0x00])
    right(8); loop_open(); dec(); left(7); inc(); right(40); inc(); left(33); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    right(40); dec(); left(40)

def compile_bracket_close():
    right(8); loop_open(); dec(); left(7); inc(); right(1); inc(); left(2); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    right(40); loop_open(); dec(); left(39); dec(); right(39); loop_close(); left(40)
    right(1); inc(2); left(1)
    right(2); inc(256); left(2)
    right(1); loop_open(); dec(); right(1); dec(); left(1); loop_close(); left(1)
    append_safe([0xeb])
    right(BUFFER_BASE); loop_open(); right(2); loop_close(); inc(); right(1); clear()
    left(BUFFER_BASE + 2); right(2)
    loop_open(); dec(); left(2); right(BUFFER_BASE); loop_open(); right(2); loop_close(); right(); inc(); left(); loop_open(); left(2); loop_close(); left(BUFFER_BASE); right(2); loop_close()
    left(2)
    right(BUFFER_BASE); loop_open(); right(2); loop_close(); right(1); clear(); left(2); loop_open(); left(2); loop_close(); left(WALL_POS); right(8); inc(); left(8)
    patch_c40_with_diff()

def patch_c40_with_diff():
    # 1. Calculate Diff (C3)
    right(8); loop_open(); dec(); left(5); inc(); right(5); loop_close(); left(8)
    right(1); loop_open(); dec(); left(1); inc(); right(8); inc(); left(8); loop_close(); left(1)
    right(40); loop_open(); dec(); left(37); dec(); right(37); loop_close(); left(40)
    right(3); dec(); left(3)
    
    # 2. Place Token at C300
    right(TOKEN_BASE); inc(); left(TOKEN_BASE)
    
    # 3. Move Token Right C40 times
    right(40); loop_open(); dec(); left(40)
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); dec(); right(2); inc(); left(2); loop_open(); left(2); loop_close(); left(TOKEN_BASE)
    right(40); loop_close(); left(40)
    
    # 4. Find Token
    right(TOKEN_BASE); loop_open(); right(2); loop_close()
    # At Token (300 track). Target is Left 199 (100 track).
    left(199)
    clear() # Clear Target
    
    # 5. [FIX] Return to Token before going Home
    right(199)
    # Scan Left to Token Wall (298)
    loop_open(); left(2); loop_close(); left(TOKEN_WALL_POS)
    
    # 6. Move C3 (Diff) to C4
    right(3); loop_open(); dec(); right(1); inc(); left(1); loop_close(); left(3)
    
    # 7. Add C4 to Target
    # Find Token again
    right(TOKEN_BASE); loop_open(); right(2); loop_close()
    left(199) # Go to Target
    
    # Add C4
    # Go back to C4
    right(199); loop_open(); left(2); loop_close(); left(TOKEN_WALL_POS); right(4)
    # Loop C4: Dec, Go Target, Inc, Go Back
    loop_open()
    dec(); left(4); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199)
    inc()
    right(199); loop_open(); left(2); loop_close(); left(TOKEN_WALL_POS); right(4)
    loop_close()
    left(4)
    
    # 8. Clear Token
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); clear(); loop_open(); left(2); loop_close(); left(TOKEN_BASE)

def check_char(char_code, logic_func):
    copy_c0_to_c1()
    right(1); dec(char_code)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(3); logic_func(); right(3); clear(); loop_close(); left(3)

def main():
    target_file_size = 500
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
        *p64(target_file_size), *p64(0x10000), *p64(0x1000)
    ]
    emit_bytes(header + prog_header)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    right(WALL_POS); clear(); right(); inc(255); left(100)
    right(TOKEN_WALL_POS); clear(); left(TOKEN_WALL_POS)
    right(BUFFER_BASE); clear(); left(BUFFER_BASE)
    right(2); clear(); inc(); left(2)
    right(2); loop_open(); left(2)
    clear(); inp()
    copy_c0_to_c1()
    right(3); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(1); clear(); right(1); clear(); loop_close(); left(3)
    check_char(62, lambda: append_safe([0x48, 0xff, 0xc3]))
    check_char(60, lambda: append_safe([0x48, 0xff, 0xcb]))
    check_char(43, lambda: append_safe([0xfe, 0x03]))
    check_char(45, lambda: append_safe([0xfe, 0x0b]))
    check_char(46, lambda: append_safe([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]))
    check_char(44, lambda: append_safe([0xb8, 0x00, 0x00, 0x00, 0x00, 0xbf, 0x00, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]))
    check_char(91, lambda: compile_bracket_open())
    check_char(93, lambda: compile_bracket_close())
    right(2); loop_close(); left(2)
    right(BUFFER_BASE)
    loop_open(); right(1); out(); right(1); loop_close()
    left(2); loop_open(); left(2); loop_close(); left(WALL_POS)
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    emit_bytes([0] * 1000)

if __name__ == "__main__":
    main()
