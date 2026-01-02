#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Spaces Compiler Generator (Level 0.8: Lightweight BF to ELF Compiler)
# Fix 1: Explicitly CLEAR C0 before inp() because 'read' syscall doesn't zero-out on EOF.
#        This prevents the infinite loop that created the 2.5MB file.
# Fix 2: Corrected pointer arithmetic inside match handlers (C5->C0 is left(5), not left(3)).

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

def emit_byte_tracked(val):
    # Output byte (C0 -> C9 -> C0)
    right(9); clear(); inc(val); out(); clear(); left(9)
    # Increment Counter C7 (C0 -> C7 -> C0)
    right(7); inc(); left(7)
    # Return to C0

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
    # C2: Loop Flag
    right(2); clear(); inc(); loop_start(); left(2) # Infinite loop until break

    # [FIX 1] Clear C0 before reading!
    # If read() returns 0 bytes (EOF), C0 must be 0 for the EOF check to work.
    clear()
    inp()
    
    # Check EOF (0)
    # Clear C1 (Scratch)
    right(); clear(); left()
    
    # Copy C0->C3 (Using C1 as scratch)
    # C0 to C3 copy
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    
    # Check if C3 is 0 (it is copy of C0)
    # If C0==0, C3==0. We want Flag(C1)=1.
    # Logic: Set C1=1. If C3!=0, Set C1=0.
    right(); inc(); right(2); loop_start(); left(2); clear(); right(2); clear(); loop_end()
    
    # If Flag(C1)==1 (EOF), Break Main Loop (C2=0)
    # We are at C3.
    left(2); loop_start(); clear(); right(); clear(); left(); loop_end(); left() # Back to C0
    
    # Check '+' (43)
    right(2); loop_start(); left(2) # If C2 is active
    
    # Clear C1
    right(); clear(); left()
    
    # Copy C0->C3
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    
    # Check if C3 == 43
    right(3); dec(43); right(2); clear(); inc(); left(2); loop_start(); right(2); clear(); left(2); clear(); loop_end()
    
    # If Match (C5=1), Emit "inc rbx"
    # We are at C3. Flag is at C5.
    right(2); loop_start()
    clear() # Clear Flag
    # [FIX 2] Go to C0. From C5, left(5) -> C0.
    left(5)
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3)
    right(5) # Back to C5
    loop_end(); left(5) # Back to C0
    
    right(2); loop_end(); left(2)

    # Check '-' (45)
    right(2); loop_start(); left(2) # If C2 is active
    
    right(); clear(); left()
    
    # Copy C0->C3
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    
    # Check if C3 == 45
    right(3); dec(45); right(2); clear(); inc(); left(2); loop_start(); right(2); clear(); left(2); clear(); loop_end()
    
    # If Match (C5=1), Emit "dec rbx"
    right(2); loop_start()
    clear()
    left(5)
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xcb)
    right(5)
    loop_end(); left(5)
    
    right(2); loop_end(); left(2)

    right(2); loop_end(); left(2) # End Main Loop

    # 4. Exit Sequence
    # mov edi, ebx; mov eax, 60; syscall
    emit_machine_code_tracked([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 5. Pad to 200 bytes
    right(7); dec(200); loop_start(); inc(200); left(7); emit_byte_tracked(0); right(7); dec(200); loop_end(); inc(200); left(7)

    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))

if __name__ == '__main__':
    main()
