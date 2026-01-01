#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: Corrected Python IndentationError.
#      Ensures ELF binary is padded to exactly 32KB (0x8000) to match headers.

import sys

# --- Constants ---
S = " "      # Space
F = "\u3000" # Fullwidth Space
CMDS = []

# --- Basic Instructions ---
def emit(s): CMDS.append(s)
def right(n=1): emit((S+S+S)*n)
def left(n=1): emit((S+S+F)*n)
def inc(n=1): emit((S+F+S)*n)
def dec(n=1): emit((S+F+F)*n)
def out(): emit(F+S+S)
def inp(): emit(F+S+F)
def loop_start(): emit(F+F+S)
def loop_end(): emit(F+F+F)

# --- Helpers ---
def clear(): 
    loop_start()
    dec()
    loop_end()

# --- TRACKED OUTPUT SYSTEM ---
# C7: Low Byte Counter, C8: High Byte Counter, C9: Scratch
# C0: Working Cursor

def emit_byte_tracked(val):
    # 1. Output byte
    right(9); clear(); inc(val); out(); clear(); left(9)
    
    # 2. Increment Counter (C7/C8)
    right(7); inc()
    
    # Check for overflow (256 -> 0) using C9
    right(2); clear(); left(2) # Clear C9
    # Copy C7 to C9
    loop_start(); right(2); inc(); left(2); dec(); loop_end()
    right(2); loop_start(); left(2); inc(); right(2); dec(); loop_end()
    
    # If C9 is 0, it was overflow (C7 wrapped to 0)
    # Logic: Set C1=1. If C9!=0, Set C1=0.
    left(9) # At C0. C1 is scratch.
    right(); clear(); inc() # C1=1
    right(8) # At C9
    
    loop_start() # If C9!=0
    left(8); clear() # C1=0
    right(8); clear() # Clear C9
    loop_end()
    
    left(8) # At C1
    loop_start() # If C1==1 (Overflow happened)
    clear()
    right(7); inc(); left(7) # Increment C8
    loop_end()
    
    left() # Back to C0

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list:
        emit_byte_tracked(b)

def main():
    # 1. Safety Margin
    right(10)

    # 2. ELF Header (64-bit Linux)
    # p_filesz = 0x8000 (32768 bytes)
    # p_memsz = 0x20000 (131072 bytes)
    # Message Address = 0x404000 (Offset 0x4000)
    
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Filesz 0x8000
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # Memsz 0x20000
        0x00, 10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte_tracked(b)

    # 3. Init Code
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte_tracked(b)

    # 4. COMPILER LOGIC
    def emit_read_token_logic():
        right(4); clear(); left(4)
        right(5); clear(); left(5)
        right(2); clear(); inc(); loop_start(); left(2)
        
        inp() # Read C0
        
        # Check EOF(0)
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); inc(); right(2); clear(); inc(); left(2); dec()
        loop_start(); right(2); clear(); left(2); clear(); loop_end()
        right(2); loop_start(); clear(); right(); inc(); left(2); dec(); right(); loop_end(); left(3)
        
        # Check S(32)
        right(2); loop_start(); left(2)
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); dec(32); right(2); clear(); inc(); left(2)
        loop_start(); right(2); clear(); left(2); clear(); loop_end()
        right(2); loop_start(); clear(); left(); dec(); right(); loop_end(); left(3)
        right(2); loop_end(); left(2)
        
        # Check F(227)
        right(2); loop_start(); left(2)
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); dec(227); right(2); clear(); inc(); left(2)
        loop_start(); right(2); clear(); left(2); clear(); loop_end()
        right(2); loop_start(); clear(); right(2); inc(); left(2); left(3); inp(); inp(); right(3); left(); dec(); right(); loop_end(); left(3)
        right(2); loop_end(); left(2)
        
        # Loop End C2
        right(2); loop_end(); left(2)

    # 5. MAIN LOOP
    right(6); clear(); left(6)
    right(2); clear(); inc(); loop_start(); left(2)
    
    right(6); clear(); left(6)
    emit_read_token_logic()
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(4); left(); loop_end(); left(5)
    
    emit_read_token_logic()
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(2); left(); loop_end(); left(5)
    
    emit_read_token_logic()
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(1); left(); loop_end(); left(5)
    
    # Message Address: 0x404000
    msg_addr = 0x404000
    addr_bytes = [(msg_addr >> (8*i)) & 0xFF for i in range(8)]
    
    right(6); inc()
    loop_start(); dec(); loop_start(); dec(); loop_start(); dec(); loop_start()
    dec(); loop_start(); dec(); loop_start(); dec(); loop_start(); dec(); loop_start()
    dec(); loop_start(); clear()
    loop_end(); emit_machine_code_tracked([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    loop_end(); emit_machine_code_tracked([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    loop_end()
    loop_end(); emit_machine_code_tracked([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    loop_end(); emit_machine_code_tracked([0x41, 0xfe, 0x4d, 0x00])
    loop_end(); emit_machine_code_tracked([0x41, 0xfe, 0x45, 0x00])
    loop_end(); emit_machine_code_tracked([0x49, 0xff, 0xcd])
    loop_end(); emit_machine_code_tracked([0x49, 0xff, 0xc5])
    left(6)
    right(2); loop_end(); left(2)

    # 6. PADDING PHASE 1: Pad until 16KB (0x4000) for Message
    # Target C8 == 64
    right(8); dec(64)
    loop_start()
    inc(64); left(8); emit_byte_tracked(0); right(8); dec(64)
    loop_end()
    inc(64); left(8)

    # 7. EMIT MESSAGE
    msg = [
        0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, # Hello, 
        0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21, 0x0a  # world!\n
    ]
    for b in msg: emit_byte_tracked(b)

    # 8. PADDING PHASE 2: Pad until 32KB (0x8000)
    # Target C8 == 128
    right(8); dec(128)
    loop_start()
    inc(128); left(8); emit_byte_tracked(0); right(8); dec(128)
    loop_end()
    inc(128); left(8)

    # Output
    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    
    # CI Log
    with open("bf_debug.log", "w") as f:
        f.write("Direct Generation Complete.\n")

if __name__ == '__main__':
    main()
