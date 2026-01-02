#!/usr/bin/env python3
# tools/gen_compiler_loop.py
# Level 1.0: The Real Loop Compiler
#
# Generates a Spaces program that:
# 1. Emits ELF Header.
# 2. Enters Main Loop (controlled by Flag C2).
# 3. Inside Loop: Read char -> Check EOF -> Check '+' -> Check '-'.
# 4. On EOF, break loop, emit Exit syscall, and pad.

import sys

# --- Spaces Ops ---
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
# C0: Input Buffer / Cursor
# C1: Scratch (Calculation)
# C2: Main Loop Flag (1 = Run, 0 = Stop)
# C3: Scratch
# C7: Output Byte Counter

def emit_byte_tracked(val):
    # Output byte val and increment C7
    # Assumes cursor is at C0. Returns to C0.
    right(8); clear(); inc(val); out(); clear(); left(8)
    right(7); inc(); left(7)

def emit_bytes(vals):
    for v in vals: emit_byte_tracked(v)

def main():
    # 1. ELF Header (Total Target: 300 bytes)
    total_size = 300
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
        *p64(total_size), *p64(total_size), *p64(0x1000)
    ]
    
    right(10) # Safety margin
    emit_bytes(header + prog_header)
    emit_bytes([0x48, 0x31, 0xdb]) # xor rbx, rbx
    
    # 2. Main Loop Setup
    # Set C2 (Flag) = 1
    right(2); clear(); inc(); left(2) # Back to C0
    
    # Enter Loop [ while C2 != 0 ]
    right(2); loop_open(); left(2) # Enter at C2, Move to C0
    
    # --- Inside Loop ---
    
    # 1. Read Char
    clear(); inp()
    
    # 2. Check EOF (Is C0 == 0?)
    # Copy C0 -> C1
    right(1); clear(); left(1)
    loop_open(); dec(); right(); inc(); left(); loop_close()
    right(); loop_open(); left(); inc(); right(); dec(); loop_close(); left() # Restore C0 from C1 (if needed for checks) and keep C1 as copy?
    # Actually, simpler: Move C0->C1. If C1 is 0, then EOF.
    # Restore: C1->C0 copy.
    # Let's do: C0 -> C1. Check C1. If C1==0 -> Clear C2 (Flag).
    # Then Restore C0 from C1 is impossible if C0 consumed.
    # Pattern: Copy C0 to C1 and C3.
    right(1); clear(); right(2); clear(); left(3) # Clear C1, C3
    loop_open(); dec(); right(); inc(); right(2); inc(); left(3); loop_close() # C0 -> C1, C3
    right(3); loop_open(); left(3); inc(); right(3); dec(); loop_close(); left(3) # Restore C0 from C3
    
    # Now C1 has the char. Check if C1 == 0.
    # We use C3 as "Is Zero Flag" (1=Yes, 0=No).
    right(3); clear(); inc(); left(3) # C3=1
    right(1) # At C1
    loop_open() 
       # If C1 is not zero, enter here.
       right(2); clear(); left(2) # Set C3=0
       clear() # Clear C1
    loop_close()
    left(1) # Back to C0
    
    # If C3 == 1 (EOF), Clear C2 (Main Loop Flag)
    right(3)
    loop_open()
       left(); clear(); right() # Clear C2
       clear() # Clear C3
    loop_close()
    left(3) # Back to C0
    
    # 3. Check '+' (43) - Only if C2 is still 1?
    # Actually, if C2 is 0, we can still run checks, they just won't match 0.
    # But strictly, we should probably guard.
    # Let's just check normally. C0 has char.
    
    # Copy C0 -> C1
    right(1); clear(); left(1)
    loop_open(); dec(); right(); inc(); right(); inc(); left(2); loop_close()
    right(2); loop_open(); left(2); inc(); right(2); dec(); loop_close(); left(2)
    
    right(); dec(43) # C1 -= 43
    # Check if C1 is 0 (Match) -> Set C3=1
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    
    # If Match (C3==1), Emit
    right(2)
    loop_open()
       left(3) # Go to C0
       emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3)
       right(3)
       clear()
    loop_close()
    left(2); left() # Back to C0

    # 4. Check '-' (45)
    right(1); clear(); left(1)
    loop_open(); dec(); right(); inc(); right(); inc(); left(2); loop_close()
    right(2); loop_open(); left(2); inc(); right(2); dec(); loop_close(); left(2)
    
    right(); dec(45)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    
    right(2)
    loop_open()
       left(3)
       emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xcb)
       right(3)
       clear()
    loop_close()
    left(2); left() # Back to C0
    
    # --- End Loop ---
    right(2); loop_close(); left(2) # Check C2, Loop Back
    
    # 3. Exit Code
    emit_bytes([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    
    # 4. Padding (C7 -> 300)
    right(7); dec(300)
    loop_open()
       inc(300); left(7)
       # Emit 0 manually
       right(8); clear(); out(); left(8); right(7); inc()
       left(7); right(7); dec(300)
    loop_close()

if __name__ == "__main__":
    main()
