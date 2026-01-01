#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: REMOVED ALL INDENTATION LOGIC to prevent Python errors.
# Fix: ADDED SAFETY COUNTERS to force-exit infinite loops (Max 256 instructions).
# Fix: Reduced file size to 4KB for instant padding.

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
# C7: Low Byte Counter, C8: High Byte Counter
# C0: Working Cursor

def emit_byte_tracked(val):
    # Output byte
    right(9); clear(); inc(val); out(); clear(); left(9)
    # Increment Counter (C7)
    right(7); inc()
    # Check Overflow C7 (256->0)
    right(2); clear(); left(2); loop_start(); right(2); inc(); left(2); dec(); loop_end(); right(2); loop_start(); left(2); inc(); right(2); dec(); loop_end()
    # If C9==0, increment C8. Use C1 as flag.
    left(9); right(); clear(); inc(); right(8); loop_start(); left(8); clear(); right(8); clear(); loop_end()
    left(8); loop_start(); clear(); right(7); inc(); left(7); loop_end()
    left() # Back to C0

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list:
        emit_byte_tracked(b)

def main():
    # 1. Safety Margin (Using up to C15)
    right(16)

    # 2. ELF Header (64-bit Linux)
    # Filesz: 0x1000 (4096 bytes)
    # Memsz: 0x20000 (131072 bytes)
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
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Filesz 4KB
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # Memsz 131KB
        0x00, 10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte_tracked(b)

    # 3. Init Code
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte_tracked(b)

    # 4. COMPILER LOGIC
    # C14: Main Instruction Safety Counter
    # C15: Token Search Safety Counter
    
    # Helper to read token: Reads until S, F, or EOF found.
    # Checks C15 limit.
    def emit_read_token_logic():
        right(4); clear(); left(4) # Clear EOF
        right(5); clear(); left(5) # Clear Result
        right(2); clear(); inc(); loop_start(); left(2) # Start C2 Loop
        
        # SAFETY CHECK C15
        right(15); inc()
        # If C15 wrapped (was 255), force break.
        right(2); clear(); left(2); loop_start(); right(2); inc(); left(2); dec(); loop_end(); right(2); loop_start(); left(2); inc(); right(2); dec(); loop_end()
        left(17); right(); clear(); inc(); right(16); loop_start(); left(17); clear(); right(17); clear(); loop_end()
        left(17); loop_start(); clear(); left(13); dec(); right(13); loop_end(); left() # If Limit, Set C4=1 (EOF), Break C2
        
        inp() # Read C0
        
        # Check EOF(0)
        right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); inc(); right(2); clear(); inc(); left(2); dec(); loop_start(); right(2); clear(); left(2); clear(); loop_end()
        right(2); loop_start(); clear(); right(); inc(); left(2); dec(); right(); loop_end(); left(3)
        
        # Check S(32)
        right(2); loop_start(); left(2); right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); dec(32); right(2); clear(); inc(); left(2); loop_start(); right(2); clear(); left(2); clear(); loop_end()
        right(2); loop_start(); clear(); left(); dec(); right(); loop_end(); left(3); right(2); loop_end(); left(2)
        
        # Check F(227)
        right(2); loop_start(); left(2); right(3); clear(); left(3); loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end(); right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); dec(227); right(2); clear(); inc(); left(2); loop_start(); right(2); clear(); left(2); clear(); loop_end()
        right(2); loop_start(); clear(); right(2); inc(); left(2); left(3); inp(); inp(); right(3); left(); dec(); right(); loop_end(); left(3); right(2); loop_end(); left(2)
        
        right(2); loop_end(); left(2) # End C2

    # 5. MAIN LOOP
    right(6); clear(); left(6)
    right(14); clear(); left(14)
    right(2); clear(); inc(); loop_start(); left(2) # Infinite Main Loop
    
    # SAFETY CHECK C14 (Total Instructions)
    right(14); inc()
    right(2); clear(); left(2); loop_start(); right(2); inc(); left(2); dec(); loop_end(); right(2); loop_start(); left(2); inc(); right(2); dec(); loop_end()
    left(16); right(); clear(); inc(); right(15); loop_start(); left(16); clear(); right(16); clear(); loop_end()
    left(16); loop_start(); clear(); left(14); dec(); right(14); loop_end(); left(2) # If Limit, Break C2
    
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
    
    # Message Address: 0x400E00 (Near end of 4KB)
    msg_addr = 0x400E00
    addr_bytes = [(msg_addr >> (8*i)) & 0xFF for i in range(8)]
    
    right(6); inc()
    loop_start() 
    dec(); loop_start() 
    dec(); loop_start() 
    dec(); loop_start() 
    dec(); loop_start() 
    dec(); loop_start() 
    dec(); loop_start() 
    dec(); loop_start() 
    clear()
    loop_end(); emit_machine_code_tracked([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    loop_end(); emit_machine_code_tracked([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    loop_end()
    loop_end(); emit_machine_code_tracked([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba] + addr_bytes + [0xba, 0x0e, 0x00, 0x00, 0x00, 0x0f, 0x05, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x31, 0xff, 0x0f, 0x05])
    loop_end(); emit_machine_code_tracked([0x41, 0xfe, 0x4d, 0x00])
    loop_end(); emit_machine_code_tracked([0x41, 0xfe, 0x45, 0x00])
    loop_end(); emit_machine_code_tracked([0x49, 0xff, 0xcd])
    loop_end(); emit_machine_code_tracked([0x49, 0xff, 0xc5])
    left(6)
    
    right(2); loop_end(); left(2)

    # 6. PADDING to 0xE00 (3584 bytes) for Message
    # Target C8 == 14 (0x0E)
    right(8); dec(14); loop_start(); inc(14); left(8); emit_byte_tracked(0); right(8); dec(14); loop_end(); inc(14); left(8)

    # 7. EMIT MESSAGE
    msg = [0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21, 0x0a]
    for b in msg: emit_byte_tracked(b)

    # 8. PADDING to 0x1000 (4096 bytes)
    # Target C8 == 16 (0x10)
    right(8); dec(16); loop_start(); inc(16); left(8); emit_byte_tracked(0); right(8); dec(16); loop_end(); inc(16); left(8)

    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    with open("bf_debug.log", "w") as f: f.write("Direct Generation Complete.\n")

if __name__ == '__main__':
    main()
