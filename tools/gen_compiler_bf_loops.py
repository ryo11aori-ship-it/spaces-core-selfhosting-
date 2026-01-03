#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 2.0: 32-bit Jumps & Padding (Flat Indent Fix)

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

WALL_POS = 98
BUFFER_BASE = 100
TOKEN_WALL_POS = 298
TOKEN_BASE = 300
TOKEN_DELTA = TOKEN_BASE - TOKEN_WALL_POS

def emit_byte_tracked(val):
    right(8); clear()
    if val > 0: inc(val)
    out(); clear(); left(8)
    right(7); inc(); left(7)

def emit_bytes(vals):
    for v in vals: emit_byte_tracked(v)

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
    # cmp byte [rbx], 0; je near +0000 (0x0f 0x84 ...)
    append_safe([0x80, 0x3b, 0x00, 0x0f, 0x84, 0x00, 0x00, 0x00, 0x00])
    
    # Push Stack
    right(8); loop_open(); dec(); left(7); inc(); right(40); inc(); left(33); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    
    # Place Token (Marker)
    right(40); dec(); left(40)
    right(TOKEN_BASE); inc(); left(TOKEN_BASE)
    right(40); loop_open(); dec(); left(40)
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); dec(); right(2); inc(); left(2); loop_open(); left(2); loop_close(); left(TOKEN_BASE)
    right(40); loop_close(); left(40)
    
    # Move Token Left 4 bytes (to point to Low Byte of offset)
    # Simplified: We rely on patch logic to find the token.
    pass

def compile_bracket_close():
    # jmp near -0000 (0xe9 ...)
    append_safe([0xe9, 0x00, 0x00, 0xff, 0xff])
    
    # Patch Open Bracket (JE)
    # Add 4 to correction (for the offset bytes themselves)
    patch_16bit_diff(4) 
    
    # Pop Stack
    right(40); loop_open(); dec(); left(39); dec(); right(39); loop_close(); left(40)
    # Clear Token
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); clear(); loop_open(); left(2); loop_close(); left(TOKEN_BASE)

def patch_16bit_diff(correction):
    # 1. Go to Token
    right(TOKEN_BASE); loop_open(); right(2); loop_close()
    left(199) 
    
    # 2. Init Counters C3, C4 with correction
    left(TOKEN_DELTA); right(3); clear(); inc(correction); right(1); clear(); left(4); right(TOKEN_DELTA)
    
    # 3. Move Token to End (Wall 199), counting steps
    loop_open()
    # Move Token Right
    dec(); right(2); inc()
    # Go Home (Left until Wall 298)
    left(2); loop_open(); left(2); loop_close(); left(TOKEN_DELTA)
    # Inc C3 (Low Byte)
    right(3); inc()
    # Simple check for wrap around 255 not implemented in BF here due to complexity constraints.
    # We rely on the buffer size being large enough and loop size < 256 for now,
    # OR we assume standard wrapping behavior of BF (0-255).
    # Ideally we should Inc C4 if C3 wraps 0.
    left(3)
    # Return to Token
    right(TOKEN_DELTA); loop_open(); right(2); loop_close()
    loop_close()
    
    # Return to Token (Start) position logic
    left(TOKEN_DELTA); right(3)
    
    # Move C3 (Diff Low) to Target (via Token Track)
    loop_open(); dec(); left(3); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199); inc(); right(199); loop_open(); left(2); loop_close(); left(TOKEN_DELTA); right(3); loop_close()
    
    # Restore State
    left(3)

def check_char(char_code, logic_func):
    right(1); clear(); right(2); clear(); left(3)
    loop_open(); dec(); right(1); inc(); right(2); inc(); left(3); loop_close()
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(3)
    right(1); dec(char_code)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(3); logic_func(); right(3); clear(); loop_close(); left(3)

def main():
    target_file_size = 65536
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
    right(WALL_POS); clear(); right(); inc(255); left(100)
    right(TOKEN_WALL_POS); clear(); left(TOKEN_WALL_POS)
    right(BUFFER_BASE); clear(); left(BUFFER_BASE)
    right(2); clear(); inc(); left(2)
    right(2); loop_open(); left(2)
    clear(); inp()
    
    # Copy C0 to C1
    right(1); clear(); right(2); clear(); left(3)
    loop_open(); dec(); right(1); inc(); right(2); inc(); left(3); loop_close()
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(3)
    
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
    
    # Dump Buffer
    right(BUFFER_BASE)
    loop_open(); right(1); out(); right(1); loop_close()
    
    # FAST PADDING
    left(BUFFER_BASE)
    right(10); clear(); inc(240)
    loop_open()
    dec(); right(1); clear(); inc(250)
    loop_open()
    dec(); right(1); clear(); out(); left(1)
    loop_close()
    left(1)
    loop_close()
    
    left(10); left(WALL_POS)
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

if __name__ == "__main__":
    main()
