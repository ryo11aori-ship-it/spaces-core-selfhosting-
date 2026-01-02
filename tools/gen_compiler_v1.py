#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Spaces Compiler Generator (Level 0.8: Lightweight BF to ELF Compiler)
# Fix: REMOVED erroneous 'break' (dec C2) inside match handlers.
#      Now correctly processes all input characters instead of quitting after the first one.

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
    # Output byte
    right(9); clear(); inc(val); out(); clear(); left(9)
    # Increment Counter (C7)
    right(7); inc(); left(7)
    # Return to C0
    left() # Back to C0

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

    # Read Input to C0
    inp()
    
    # Check EOF (0)
    # Clear C1 before use
    right(); clear(); left()
    
    # Copy C0->C3
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    # If C0 is 0, C3 is 0. Set Flag=1 if C3=0.
    right(); inc(); right(2); clear(); inc(); left(2); dec(); loop_start(); right(2); clear(); left(2); clear(); loop_end()
    # If Flag==1 (EOF), Break Main Loop (C2=0)
    right(2); loop_start(); clear(); right(); inc(); left(2); dec(); right(); loop_end(); left(3)
    
    # Check '+' (43)
    right(2); loop_start(); left(2) # If C2 is active
    
    # Clear C1
    right(); clear(); left()
    
    # Copy C0->C3 (Using C1 as scratch in process)
    # Note: Copy logic uses C1(Right) and C3(Right(3)). 
    # Current Pos: C0. 
    # right(3) -> C3. left(3) -> C0.
    # Logic: loop C0 { dec C0; inc C1; inc C3 } -> Moves C0 to C1,C3.
    # Restore C0 from C3.
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    
    # Check if C1 == 43
    right(); dec(43); right(2); clear(); inc(); left(2); loop_start(); right(2); clear(); left(2); clear(); loop_end()
    
    # If Match (+), Emit "inc rbx" (48 ff c3)
    # We are at C3 (Match Flag).
    right(2); loop_start()
        clear() # Clear Flag
        left(3) # Go to C0 (Cursor)
        emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3)
        right(3) # Back to C3
        # [FIX] Do NOT decrement C2 here! We want to continue reading.
    loop_end(); left(3)
    
    right(2); loop_end(); left(2)

    # Check '-' (45)
    right(2); loop_start(); left(2) # If C2 is active
    
    # Clear C1
    right(); clear(); left()

    # Copy C0->C3
    right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
    
    # Check if C1 == 45
    right(); dec(45); right(2); clear(); inc(); left(2); loop_start(); right(2); clear(); left(2); clear(); loop_end()
    
    # If Match (-), Emit "dec rbx" (48 ff cb)
    right(2); loop_start()
        clear()
        left(3)
        emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xcb)
        right(3)
        # [FIX] Do NOT decrement C2 here!
    loop_end(); left(3)
    
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
