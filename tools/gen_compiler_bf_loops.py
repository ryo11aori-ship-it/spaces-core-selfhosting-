#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 2.2: Fix Segfault & Logic
# Fix: 
#  1. JMP correction set to 9 bytes (CMP+JE) to land on instruction boundary.
#  2. Implements JE patching (Forward Jump) to correct address (skip loop).

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
    # 3 bytes (cmp) + 6 bytes (je) = 9 bytes total overhead at start
    append_safe([0x80, 0x3b, 0x00, 0x0f, 0x84, 0x00, 0x00, 0x00, 0x00])
    
    # Push Stack
    right(8); loop_open(); dec(); left(7); inc(); right(40); inc(); left(33); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    
    # Place Token at Body Start
    right(40); dec(); left(40)
    right(TOKEN_BASE); inc(); left(TOKEN_BASE)
    right(40); loop_open(); dec(); left(40)
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); dec(); right(2); inc(); left(2); loop_open(); left(2); loop_close(); left(TOKEN_BASE)
    right(40); loop_close(); left(40)

def compile_bracket_close():
    # jmp near -0000 (0xe9 ...)
    append_safe([0xe9, 0x00, 0x00, 0xff, 0xff])
    
    # Patch Both Directions
    patch_bidirectional()
    
    # Pop Stack
    right(40); loop_open(); dec(); left(39); dec(); right(39); loop_close(); left(40)
    # Clear Token
    right(TOKEN_BASE); loop_open(); right(2); loop_close(); clear(); loop_open(); left(2); loop_close(); left(TOKEN_BASE)

def patch_bidirectional():
    # 1. Go to Token (Body Start)
    right(TOKEN_BASE); loop_open(); right(2); loop_close()
    left(199)
    
    # 2. Measure Distance D (Body + JMP instruction)
    # We move Token to End (Current), counting steps in C3.
    # C3 starts at 0.
    left(TOKEN_DELTA); right(3); clear(); left(3); right(TOKEN_DELTA)
    
    loop_open()
    dec(); right(2); inc() # Move Token Right
    left(2); loop_open(); left(2); loop_close(); left(TOKEN_DELTA)
    right(3); inc(); left(3) # Inc C3
    right(TOKEN_DELTA); loop_open(); right(2); loop_close() # Return to Token
    loop_close()
    
    # Token is now at End. C3 = D.
    
    # 3. Patch JE (Forward Jump)
    # Target: Token - 4 (Offset field of JE).
    # Value: D.
    # We are at End (Token).
    # We need to write D to (Start - 4).
    # Move C3 copy to (Start - 4).
    # First, move Token back to Start?
    # No, Token is at End. We can leave it there for a moment?
    # No, `compile_bracket_close` expects Token at End to clear it?
    # Actually `compile_bracket_close` cleans up Token.
    
    # Move C3 value to "Temp at End"?
    # We need to traverse back to Start.
    # We don't have a marker at Start anymore (Token moved).
    # WAIT. If I move Token, I lose the Start position!
    # I should have left a shadow copy?
    # Or I should move it back?
    # Yes, move Token back to Start.
    
    # Move Token Left D steps.
    # Use C3 as counter.
    left(TOKEN_DELTA); right(3)
    loop_open()
      dec()
      left(3); right(TOKEN_DELTA); loop_open(); right(2); loop_close(); left(199)
      # At Token (End). Move Left.
      dec(); left(2); inc()
      right(2); right(199); loop_open(); left(2); loop_close(); left(TOKEN_DELTA)
      right(3)
    loop_close()
    # Now Token is back at Start.
    
    # PROBLEM: We destroyed D in C3.
    # We need D to patch JE.
    # We need D+9 to patch JMP.
    
    # BETTER ALGORITHM:
    # 1. Copy C3 (D) to C4 (D_copy) and C5 (D_copy2).
    # ... (Re-measure D) ...
    # Start at Start.
    # Loop until End: Inc C3, C4. Move Token.
    # Then Loop C4: Move Token Back.
    
    # OK, implemented:
    # A. Init C3=0, C4=0.
    left(3); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199) # Go to Token (Start)
    left(TOKEN_DELTA); right(3); clear(); right(1); clear(); left(4); right(TOKEN_DELTA)
    
    # B. Measure D. Move Token to End.
    loop_open()
      dec(); right(2); inc() # Move Token
      left(2); loop_open(); left(2); loop_close(); left(TOKEN_DELTA)
      right(3); inc(); right(1); inc(); left(4) # Inc C3, C4
      right(TOKEN_DELTA); loop_open(); right(2); loop_close()
    loop_close()
    # Token at End. C3=D, C4=D.
    
    # C. Patch JMP (Backward).
    # Location: End - 4.
    # Value: -(D + 9).
    # Calculate Val = 256 - (D + 9).
    # D is in C3.
    # C3 = C3 + 9.
    left(TOKEN_DELTA); right(3); inc(9)
    # Temp C2 = 256.
    left(1); clear(); inc(256)
    # Sub C3 from C2.
    right(1); loop_open(); dec(); left(1); dec(); right(1); loop_close()
    # C2 has -(D+9).
    left(1)
    # Write C2 to End-4.
    # We are at C2. Token is at End.
    # Move C2 to Token-4 via buffer logic.
    loop_open(); dec(); right(1); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199); left(4); inc(); right(4); right(199); loop_open(); left(2); loop_close(); left(TOKEN_DELTA); left(1); loop_close()
    # JMP Patched.
    
    # D. Patch JE (Forward).
    # Location: Start - 4.
    # Value: D (in C4).
    # First, move Token back to Start using C4 count.
    # AND carry C4 value (restore it) or copy it?
    # We need C4 value to write.
    # Use C4 to move Token back, but we execute the "Write" at the end?
    # No, write D to Token-4.
    # Token is currently at End.
    # Move Token Left 1, Dec C4. REPEAT until C4=0? No we lose D.
    
    # Copy C4 to C5.
    right(4); loop_open(); dec(); right(1); inc(); right(1); inc(); left(2); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    # C4 restored, C5 has D.
    
    # Use C5 to move Token Back.
    right(1)
    loop_open()
      dec()
      left(5); right(TOKEN_DELTA); loop_open(); right(2); loop_close(); left(199)
      dec(); left(2); inc() # Move Token Left
      right(2); right(199); loop_open(); left(2); loop_close(); left(TOKEN_DELTA); right(5)
    loop_close()
    # Token is back at Start.
    
    # Use C4 (D) to patch Token-4.
    left(1)
    loop_open(); dec(); right(1); right(TOKEN_BASE); loop_open(); right(2); loop_close(); left(199); left(4); inc(); right(4); right(199); loop_open(); left(2); loop_close(); left(TOKEN_DELTA); left(4); loop_close()
    
    # Done.
    left(3)

def copy_c0_to_c1():
    right(1); clear(); right(2); clear(); left(3)
    loop_open(); dec(); right(1); inc(); right(2); inc(); left(3); loop_close()
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(3)

def check_char(char_code, logic_func):
    copy_c0_to_c1()
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
    
    # Padding
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
