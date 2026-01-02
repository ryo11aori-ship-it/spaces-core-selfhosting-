#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Spaces Compiler Generator (Level 0.8: Lightweight BF to ELF Compiler)
# Fix: Corrected Logic Flow for EOF check and Char matching.
#      Previous version destroyed data before checking, leading to false EOF.

import sys

def p64(val): return list(val.to_bytes(8, 'little'))
def p32(val): return list(val.to_bytes(4, 'little'))

# --- Constants ---
S = " "
F = "\u3000"
CMDS = []

def emit(s): CMDS.append(s)
def right(n=1): emit((S+S+S)*n)
def left(n=1): emit((S+S+F)*n)
def inc(n=1): emit((S+F+S)*n)
def dec(n=1): emit((S+F+F)*n)
def out(): emit(F+S+S)
def inp(): emit(F+S+F)
def loop_start(): emit(F+F+S)
def loop_end(): emit(F+F+F)
def clear(): loop_start(); dec(); loop_end()

# --- Simplified Tracked Output (1 Byte Only) ---
# C0: Working Cursor
# C7: Byte Counter (Max 255)
# C9: Scratch for output

def emit_byte_tracked(val):
    # Output byte (C0 -> C9 -> C0)
    right(9); clear(); inc(val); out(); clear(); left(9)
    # Increment Counter C7 (C0 -> C7 -> C0)
    right(7); inc(); left(7)

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list: emit_byte_tracked(b)

def main():
    right(16) # Safety margin

    # 1. Emit ELF Header (Target Total Size: 200 bytes)
    load_addr = 0x400000
    header_len = 120
    total_size = 200 # 0xC8
    
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        *p64(load_addr + header_len), *p64(64), *p64(0), *p32(0),
        0x40, 0x00, 0x38, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    prog_header = [
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(total_size), *p64(total_size), *p64(0x1000)
    ]
    for b in header + prog_header: emit_byte_tracked(b)

    # 2. Init Code: xor rbx, rbx
    emit_machine_code_tracked([0x48, 0x31, 0xdb])

    # 3. Main Loop
    # C2: Loop Flag (1 = Running)
    right(2); clear(); inc(); loop_start(); left(2) 

    # Read Input to C0
    # Clear C0 first because inp() behavior on EOF is to leave cell unchanged
    clear()
    inp()
    
    # --- LOGIC START: COPY & CHECK PATTERN ---
    # We need to preserve C0 for multiple checks (+, -).
    # Pattern: Copy C0 -> C1 & C3. Check C3. Restore C0 from C1.
    
    # 1. Check EOF (Is C0 == 0?)
    # Clear C1, C3
    right(); clear(); right(2); clear(); left(3)
    
    # Copy C0 -> C1 & C3
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    
    # Check C3. If C3==0, it's EOF.
    # We use C5 as "Is Zero Flag". Set C5=1.
    right(5); clear(); inc(); left(5)
    # If C3 != 0, Set C5=0.
    right(3); loop_start(); clear(); right(2); clear(); left(2); loop_end(); left(3)
    
    # If C5==1 (EOF), Break C2 Loop.
    right(5); loop_start(); clear(); left(3); dec(); right(3); loop_end(); left(5)
    
    # Restore C0 from C1 (Only if not broken, but broken loop won't exec this effectively)
    right(); loop_start(); dec(); left(); inc(); right(); loop_end(); left()
    
    
    # 2. Check '+' (43)
    # Check if loop C2 is still active
    right(2); loop_start(); left(2)
    
    # Clear C1, C3
    right(); clear(); right(2); clear(); left(3)
    # Copy C0 -> C1 & C3
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    
    # Sub 43 from C3
    right(3); dec(43); left(3)
    
    # Check if C3 == 0 (Match).
    # Set C5=1 (Match Flag).
    right(5); clear(); inc(); left(5)
    # If C3 != 0, Set C5=0.
    right(3); loop_start(); clear(); right(2); clear(); left(2); loop_end(); left(3)
    
    # If Match (C5==1), Emit Bytes
    right(5); loop_start()
    clear() # Clear match flag
    left(5) # Go to C0
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3)
    right(5) # Back to C5
    loop_end(); left(5)
    
    # Restore C0 from C1
    right(); loop_start(); dec(); left(); inc(); right(); loop_end(); left()
    
    right(2); loop_end(); left(2) # End C2 check


    # 3. Check '-' (45)
    # Check if loop C2 is still active
    right(2); loop_start(); left(2)
    
    # Clear C1, C3
    right(); clear(); right(2); clear(); left(3)
    # Copy C0 -> C1 & C3
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    
    # Sub 45 from C3
    right(3); dec(45); left(3)
    
    # Check if C3 == 0 (Match).
    right(5); clear(); inc(); left(5)
    right(3); loop_start(); clear(); right(2); clear(); left(2); loop_end(); left(3)
    
    # If Match (C5==1), Emit Bytes
    right(5); loop_start()
    clear()
    left(5) # Go to C0
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xcb)
    right(5)
    loop_end(); left(5)
    
    # Restore C0 from C1
    right(); loop_start(); dec(); left(); inc(); right(); loop_end(); left()
    
    right(2); loop_end(); left(2) # End C2 check


    right(2); loop_end(); left(2) # End Main Loop

    # 4. Exit Sequence
    emit_machine_code_tracked([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 5. Pad to 200 bytes
    right(7); dec(200); loop_start(); inc(200); left(7); emit_byte_tracked(0); right(7); dec(200); loop_end(); inc(200); left(7)

    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))

if __name__ == '__main__':
    main()
