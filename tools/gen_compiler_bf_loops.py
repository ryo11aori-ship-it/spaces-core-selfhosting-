#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler with Long Jumps (32-bit offsets)
# Fix: Replaced Short Jumps (EB/74) with Long Jumps (E9/0F84) to handle large loops in self-hosting.
#      Implemented 32-bit Little Endian Patching logic in raw Spaces.

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

def emit_bytes(vals):
    for v in vals:
        right(8); clear()
        if v > 0: inc(v)
        out(); clear(); left(8)
        right(7); inc(); left(7)

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

def append_from_c5():
    right(BUFFER_BASE)
    loop_open(); right(2); loop_close()
    inc()
    right(1); clear()
    left(BUFFER_BASE+1); right(5)
    loop_open(); dec(); left(5); left(WALL_POS); right(BUFFER_BASE); loop_open(); right(2); loop_close(); right(); inc(); left(); loop_open(); left(2); loop_close(); left(BUFFER_BASE); right(WALL_POS); right(5)
    loop_close()
    left(5)
    right(BUFFER_BASE); loop_open(); right(2); loop_close(); right(2); clear(); left(2); loop_open(); left(2); loop_close(); left(WALL_POS); right(8); inc(); left(8)

def compile_bracket_open():
    right(8); loop_open(); dec(); left(7); inc(); right(40); inc(); left(33); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    append_safe([0x80, 0x3b, 0x00])
    append_safe([0x0f, 0x84, 0x00, 0x00, 0x00, 0x00])

def compile_bracket_close():
    append_safe([0xe9])
    right(8); loop_open(); dec(); left(7); inc(); right(1); inc(); left(2); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    right(1); inc(5); left(1)
    right(40); loop_open(); dec(); left(39); dec(); right(39); loop_close(); left(40)
    right(2); clear(); right(1); clear(); right(1); clear(); inc(256); left(4)
    right(1)
    loop_open()
    dec(); right(2); inc(); right(1); dec()
    right(1); clear(); left(1); loop_open(); dec(); right(); inc(); left(); loop_close(); right(); loop_open(); dec(); left(); inc(); right(); loop_close(); left(1)
    right(1); right(1); clear(); inc(); left(1); loop_open(); right(); clear(); left(); clear(); loop_close(); right()
    loop_open(); left(2); inc(256); right(2); left(3); clear(); right(3); left(4); inc(); right(4); clear(); loop_close(); left(5)
    loop_close()
    left(1)
    right(3); loop_open(); dec(); right(2); inc(); left(2); loop_close(); left(3)
    right(5); right(1); clear(); inc(); left(1); loop_open(); right(); clear(); left(); clear(); loop_close(); right()
    left(1)
    right(2); inc(256); left(2)
    loop_open(); dec(); right(2); dec(); left(2); loop_close()
    right(1); loop_open(); right(1); clear(); left(1); dec(); loop_close(); left(1)
    right(2); loop_open(); dec(); right(2); inc(); left(2); loop_close(); left(2)
    right(4); loop_open(); dec(); left(2); inc(); right(2); loop_close(); left(4)
    right(8); inc(255); left(8)
    right(4); loop_open(); dec(); right(4); dec(); left(4); loop_close(); left(4)
    right(6); loop_open(); dec(); right(2); inc(); left(2); loop_close(); left(6)
    right(7); loop_open(); dec(); left(2); inc(); right(2); loop_close(); left(7)
    append_from_c5()
    right(8); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(8)
    append_from_c5()
    append_safe([255, 255])
    right(8); loop_open(); dec(); left(7); inc(); right(1); inc(); left(2); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    right(40); loop_open(); dec(); left(39); dec(); right(39); loop_close(); left(40)
    right(1); dec(9); left(1)
    right(1); loop_open(); dec(); right(4); inc(); left(4); loop_close(); left(1)
    right(40); loop_open(); dec(); left(34); inc(); right(34); loop_close(); left(40)
    right(1); loop_open(); dec(); left(1); inc(); right(40); inc(); left(40); loop_close(); left(1)
    right(6); inc(5); left(6)
    right(5)
    right(3); clear(); right(1); clear(); right(1); clear(); inc(256); left(5)
    loop_open()
    dec(); right(3); inc(); right(1); dec()
    right(1); clear(); left(1); loop_open(); dec(); right(); inc(); left(); loop_close(); right(); loop_open(); dec(); left(); inc(); right(); loop_close(); left(1)
    right(1); right(1); clear(); inc(); left(1); loop_open(); right(); clear(); left(); clear(); loop_close(); right()
    loop_open(); left(2); inc(256); right(2); left(3); clear(); right(3); left(4); inc(); right(4); clear(); loop_close(); left(5)
    loop_close()
    left(2); loop_open(); dec(); right(2); inc(); left(2); loop_close(); right(2)
    patch_at_c6_with_c5()
    right(6); inc(); left(6)
    right(2); loop_open(); dec(); right(3); inc(); left(3); loop_close(); left(2)
    patch_at_c6_with_c5()
    right(6); inc(); left(6); patch_at_c6_with_c5()
    right(6); inc(); left(6); patch_at_c6_with_c5()

def patch_at_c6_with_c5():
    right(TOKEN_BASE); inc(); left(TOKEN_BASE)
    right(6); loop_open(); dec(); left(6)
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); dec(); right(2); inc(); left(2); loop_open(); left(2); loop_close(); left(TOKEN_BASE)
    right(6); loop_close(); left(6)
    right(TOKEN_BASE); loop_open(); right(2); loop_close()
    left(199); clear()
    right(199); left(TOKEN_DELTA)
    right(5); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(5)
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199)
    right(199); left(TOKEN_DELTA); right(4)
    loop_open()
    dec(); left(4); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199)
    inc()
    right(199); left(TOKEN_DELTA); right(4)
    loop_close()
    left(4)
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); clear(); loop_open(); left(2); loop_close(); left(TOKEN_BASE)

def check_char(char_code, logic_func):
    copy_c0_to_c1()
    right(1); dec(char_code)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(3); logic_func(); right(3); clear(); loop_close(); left(3)

def main():
    target_file_size = 500
    total_size = 2000
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
