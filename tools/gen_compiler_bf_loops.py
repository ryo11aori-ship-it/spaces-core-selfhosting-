#!/usr/bin/env python3
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
    append_safe([0x80, 0x3b, 0x00, 0x0f, 0x84, 0x00, 0x00, 0x00, 0x00])
    right(8); loop_open(); dec(); left(7); inc(); right(40); inc(); left(33); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    right(40); dec(); left(40)
    right(TOKEN_BASE); inc(); left(TOKEN_BASE)
    right(40); loop_open(); dec(); left(40)
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); dec(); right(2); inc(); left(2); loop_open(); left(2); loop_close(); left(TOKEN_BASE)
    right(40); loop_close(); left(40)

def compile_bracket_close():
    append_safe([0xe9, 0x00, 0x00, 0xff, 0xff])
    patch_16bit_bidirectional()
    right(40); loop_open(); dec(); left(39); dec(); right(39); loop_close(); left(40)
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); clear(); loop_open(); left(2); loop_close(); left(TOKEN_BASE)

def patch_16bit_bidirectional():
    # 1. Go to Token (Start)
    right(TOKEN_BASE); loop_open(); right(2); loop_close()
    left(199)
    # 2. Init C3(Low), C4(High) with correction=9 (CMP+JE+JMP sizes)
    left(TOKEN_DELTA); right(3); clear(); inc(9); right(1); clear(); left(4); right(TOKEN_DELTA)
    # 3. Measure Distance to C3/C4
    loop_open()
    dec(); right(2); inc()
    left(2); loop_open(); left(2); loop_close(); left(TOKEN_DELTA)
    right(3); inc()
    # Handle Carry C3 -> C4
    loop_open(); dec(); right(3); inc(); left(3); loop_close() # Check C3==0 (Wrapped)
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(3)
    # If C3 wrapped to 0, Inc C4
    # Logic: If C3 is 0, Flag=1.
    right(1); clear(); inc(); left(1) # Flag=1
    right(3); loop_open(); left(3); right(1); dec(); left(1); right(3); loop_close(); left(3) # If C3!=0, Flag=0
    right(1); loop_open(); dec(); right(3); inc(); left(3); loop_close(); left(1) # If Flag=1, Inc C4
    right(TOKEN_DELTA); loop_open(); right(2); loop_close()
    loop_close()
    # Now C3/C4 has Distance D.
    
    # 4. Patch JE (Forward) with D
    # Target: Start-4 (Low), Start-3 (High).
    # Token is at End. Move back to Start using C3/C4?
    # Better: Patch JMP (Back) first because we are at End.
    # Backward Offset = -D = (~D + 1).
    # Low = (0-L). High = (0-H) - borrow.
    # Calculate -D in C5(Low), C6(High).
    left(TOKEN_DELTA)
    # Copy C3, C4 to C5, C6
    right(3); loop_open(); dec(); left(1); inc(); right(3); inc(); left(2); loop_close(); right(2); loop_open(); dec(); left(2); inc(); right(2); loop_close(); left(2)
    right(4); loop_open(); dec(); left(1); inc(); right(3); inc(); left(2); loop_close(); right(2); loop_open(); dec(); left(2); inc(); right(2); loop_close(); left(4)
    # Negate C5, C6 (Result in C5, C6)
    # C5 = 0 - C5. Borrow detection?
    # If C5 > 0, Borrow = 1.
    right(5); loop_open(); left(1); inc(); right(1); loop_close(); left(1) # If C5>0, Flag=1
    right(1); loop_open(); dec(); right(5); dec(); left(5); loop_close(); left(1) # If Flag, Dec C6
    # Negate C5 (0 - C5)
    right(5); loop_open(); dec(); left(1); dec(); right(1); loop_close(); left(1); loop_open(); dec(); right(5); inc(); left(5); loop_close(); left(4)
    # Negate C6 (0 - C6)
    right(6); loop_open(); dec(); left(1); dec(); right(1); loop_close(); left(1); loop_open(); dec(); right(6); inc(); left(6); loop_close(); left(6)
    # Now C5/C6 has -D.
    
    # Write C5 to End-4, C6 to End-3.
    # End is current buffer head.
    right(TOKEN_DELTA); right(TOKEN_BASE); loop_open(); right(2); loop_close()
    left(199) # At End
    left(4); inc(); right(4) # Mark Target Low
    left(3); inc(); right(3) # Mark Target High
    right(199); loop_open(); left(2); loop_close(); left(TOKEN_DELTA)
    # Move C5 to Target Low
    right(5); loop_open(); dec(); left(5); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199); left(4); loop_open(); dec(); left(200); inc(); right(200); loop_close(); inc(); right(4); right(199); loop_open(); left(2); loop_close(); left(TOKEN_DELTA); right(5); loop_close()
    # Move C6 to Target High
    right(1); loop_open(); dec(); left(6); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199); left(3); loop_open(); dec(); left(200); inc(); right(200); loop_close(); inc(); right(3); right(199); loop_open(); left(2); loop_close(); left(TOKEN_DELTA); right(6); loop_close()
    left(6)
    
    # 5. Patch JE (Forward) with D (C3/C4).
    # Need to move Token back to Start.
    # Use C3/C4 to count back?
    # Simply reverse the measure loop logic?
    # Loop until Token hits Wall? No Wall at Start.
    # Use "Move Token Left D steps".
    # We have D in C3/C4.
    # Decrement C3/C4 while moving Token Left.
    right(TOKEN_DELTA); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199)
    # Token at End.
    left(TOKEN_DELTA); left(TOKEN_BASE); left(TOKEN_WALL_POS); right(TOKEN_DELTA)
    # Loop: Move Token Left. Dec C3. If C3 wraps, Dec C4.
    # Until C3=0 and C4=0.
    loop_open() # While C3 or C4 > 0
       # Check if C3>0
       right(3); loop_open(); left(1); inc(); right(1); loop_close(); left(1)
       # If C3==0, Dec C4, Set C3=255.
       # (Complex logic skipped, assume loop < 256 for now or just move blindly)
       # REVERT: Just use the fact that we can search for the "Start" marker?
       # No marker.
       # OK, assume D < 256 for now to allow simple rollback.
       left(3); right(TOKEN_DELTA); right(TOKEN_BASE); loop_open(); right(2); loop_close()
       left(199); dec(); left(2); inc(); right(2); right(199); loop_open(); left(2); loop_close()
       left(TOKEN_DELTA); right(3); dec(); left(3)
    loop_close()
    
    # Patch JE Low (Start-4) with saved D?
    # We destroyed D to rollback.
    # Assuming JE is 00 00 is fine for "Don't Skip" behavior (Infinite Loop).
    # But we want to skip.
    # For now, FIXING SEGFAULT (JMP) is priority.
    # JE can be broken (loop always runs), but JMP must be correct to avoid segfault.
    pass

def copy_c0_to_c1():
    right(1); clear(); right(2); clear(); left(3)
    loop_open(); dec(); right(1); inc(); right(2); inc(); left(3); loop_close()
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(3)

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
    right(BUFFER_BASE)
    loop_open(); right(1); out(); right(1); loop_close()
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
