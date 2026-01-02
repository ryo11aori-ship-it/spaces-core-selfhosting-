#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Spaces Compiler Generator (Level 0.8: BF to ELF Compiler)
#
# Logic:
# 1. Emit ELF Header (4KB).
# 2. Emit Init (xor rbx, rbx).
# 3. Loop: Read char.
#    - If 0 (EOF): Break.
#    - If '+': Emit "inc rbx".
#    - If '-': Emit "dec rbx".
# 4. Emit Exit Sequence.
# 5. Pad to 4KB.

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

# --- Tracked Output System ---
# C0: Working Cursor
# C7: Low Byte Counter
# C8: High Byte Counter
# C9: Scratch

def emit_byte_tracked(val):
    # Output byte
    right(9); clear(); inc(val); out(); clear(); left(9)
    # Increment Counter (C7)
    right(7); inc()
    # Check Overflow C7 (256 -> 0)
    # Use C9 as check buffer
    right(2); clear(); left(2); loop_start(); right(2); inc(); left(2); dec(); loop_end(); right(2); loop_start(); left(2); inc(); right(2); dec(); loop_end()
    # If C9==0, increment C8. Use C1 as flag.
    left(9); right(); clear(); inc(); right(8); loop_start(); left(8); clear(); right(8); clear(); loop_end()
    left(8); loop_start(); clear(); right(7); inc(); left(7); loop_end(); left()

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list: emit_byte_tracked(b)

def main():
    right(16) # Safety margin

    # 1. Emit ELF Header (4KB)
    load_addr = 0x400000
    header_len = 120
    total_size = 0x1000 # 4KB
    
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

    # Read Input to C0
    inp()
    
    # Check EOF (0)
    # Copy C0->C3
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    # If C0 is 0, C3 is 0. Set Flag=1 if C3=0.
    right(); inc(); right(2); clear(); inc(); left(2); dec(); loop_start(); right(2); clear(); left(2); clear(); loop_end()
    # If Flag==1 (EOF), Break Main Loop (C2=0)
    right(2); loop_start(); clear(); right(); inc(); left(2); dec(); right(); loop_end(); left(3)
    
    # Check '+' (43)
    right(2); loop_start(); left(2) # If C2 is active
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    right(); dec(43); right(2); clear(); inc(); left(2); loop_start(); right(2); clear(); left(2); clear(); loop_end()
    # If Match (+), Emit "inc rbx" (48 ff c3)
    right(2); loop_start(); clear(); left(3); emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3); right(3); left(3); clear(); right(3); left(); dec(); right(); loop_end(); left(3)
    right(2); loop_end(); left(2)

    # Check '-' (45)
    right(2); loop_start(); left(2) # If C2 is active
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    right(); dec(45); right(2); clear(); inc(); left(2); loop_start(); right(2); clear(); left(2); clear(); loop_end()
    # If Match (-), Emit "dec rbx" (48 ff cb)
    right(2); loop_start(); clear(); left(3); emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xcb); right(3); left(3); clear(); right(3); left(); dec(); right(); loop_end(); left(3)
    right(2); loop_end(); left(2)

    right(2); loop_end(); left(2) # End Main Loop

    # 4. Exit Sequence
    # mov edi, ebx; mov eax, 60; syscall
    emit_machine_code_tracked([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 5. Pad to 4KB (0x1000 = 16 * 256)
    # Check C8. Loop until C8 == 16.
    right(8); dec(16); loop_start(); inc(16); left(8); emit_byte_tracked(0); right(8); dec(16); loop_end(); inc(16); left(8)

    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    with open("bf_debug.log", "w") as f: f.write("Generated Compiler V1 (Simplified).\n")

if __name__ == '__main__':
    main()
