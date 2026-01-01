#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: Implemented "Byte Counting & Padding" to ensure output binary is exactly 32KB.
#      This solves the Segmentation Fault caused by truncated program loading.

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
# We use C7 (Low Byte) and C8 (High Byte) to count emitted bytes.
# C0 is the working cursor.

def emit_byte_tracked(val):
    # 1. Output the byte (using C9 as scratch)
    right(9); clear(); inc(val); out(); clear(); left(9)
    
    # 2. Increment Counter (C7/C8)
    right(7); inc()
    # Check for overflow (256 -> 0)
    # Copy C7 to C9 to check
    right(2); clear(); left(2)
    loop_start(); right(2); inc(); left(2); dec(); loop_end()
    right(2); loop_start(); left(2); inc(); right(2); dec(); loop_end()
    # If C9 is 0, it was overflow.
    # Set C1=1 if C9==0.
    left(2) # At C7
    # C9 is at +2.
    right(3); clear(); left(3) # C10 as flag
    
    right(2) # At C9
    inc() # If it was 0, now 1.
    loop_start()
    clear() # It wasn't 0.
    loop_end()
    # If C9 is still 1, it was 0 (Overflow).
    loop_start()
    clear()
    left(); inc(); right() # Increment C8
    loop_end()
    
    left(9) # Back to C0

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list:
        emit_byte_tracked(b)

def main():
    # 1. Safety Margin
    right(10) # Using up to C9

    # 2. ELF Header (64-bit Linux)
    # p_filesz = 0x8000 (32768 bytes)
    # p_memsz = 0x20000 (131072 bytes) to cover BF Tape
    # Message Address = 0x404000 (Offset 0x4000 = 16384)
    
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # Entry 0x400078
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # p_filesz 0x8000
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # p_memsz 0x20000
        0x00, 10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte_tracked(b)

    # 3. Init Code
    # mov r13, 0x408000 (Tape Start)
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte_tracked(b)

    # 4. COMPILER LOGIC (Parser)
    def emit_read_token_logic():
        right(4); clear(); left(4) # C4
        right(5); clear(); left(5) # C5
        right(2); clear(); inc(); loop_start() # C2=1 Loop
        left(2); inp() # Read C0
        
        # Check EOF(0)
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); inc(); right(2); clear(); inc(); left(2); dec()
        loop_start(); right(2); clear(); left(2); clear(); loop_end()
        # If C3==1 (EOF)
        right(2); loop_start(); clear(); right(); inc(); left(2); dec(); right(); loop_end(); left(3)
        
        # Check S(32)
        right(2); loop_start(); left(2) # If C2
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); dec(32); right(2); clear(); inc(); left(2)
        loop_start(); right(2); clear(); left(2); clear(); loop_end()
        # If C3==1 (S)
        right(2); loop_start(); clear(); left(); dec(); right(); loop_end(); left(3)
        right(2); loop_end(); left(2)
        
        # Check F(227)
        right(2); loop_start(); left(2)
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        right(); dec(227); right(2); clear(); inc(); left(2)
        loop_start(); right(2); clear(); left(2); clear(); loop_end()
        # If C3==1 (F)
        right(2); loop_start(); clear(); right(2); inc(); left(2)
        left(3); inp(); inp(); right(3)
        left(); dec(); right(); loop_end(); left(3)
        right(2); loop_end(); left(2)
        
        # Loop End C2 (Garbage Check)
        right(2); loop_end(); left(2)

    # 5. MAIN LOOP
    right(6); clear(); left(6)
    right(2); clear(); inc(); loop_start(); left(2) # Infinite Loop
    
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
    
    # Dispatch
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
    loop_end(); emit_machine_code_tracked([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    loop_end(); emit_machine_code_tracked([0x41, 0xfe, 0x4d, 0x00])
    loop_end(); emit_machine_code_tracked([0x41, 0xfe, 0x45, 0x00])
    loop_end(); emit_machine_code_tracked([0x49, 0xff, 0xcd])
    loop_end(); emit_machine_code_tracked([0x49, 0xff, 0xc5])
    left(6)
    
    right(2); loop_end(); left(2)

    # 6. PADDING PHASE 1: Pad until 16KB (0x4000) for Message
    # Target C8 == 64 (64 * 256 = 16384)
    right(8) # At C8
    
    # Loop until C8 == 64
    inc() # make non-zero to enter loop check
    loop_start()
    dec() # Restore real value
    
    # Check if C8 == 64
    # Copy C8 to C9
    right(); clear(); left()
    loop_start(); right(); inc(); left(); dec(); loop_end()
    right(); loop_start(); left(); inc(); right(); dec(); loop_end()
    
    dec(64) # C8 - 64
    
    # If C8 is 0, we are done.
    right(); clear(); inc(); left() # C9=1
    loop_start(); right(); clear(); left(); clear(); loop_end() # If C8!=0, C9=0
    
    # If C9==1 (Done)
    right(); loop_start(); clear(); left(); clear(); right(); loop_end(); left()
    
    # If C8 is not 0 (Not done), we need to restore it (add 64 back) and emit 0
    # Actually, we destroyed C8.
    # Simpler approach: 
    # Just emit 0, and check C8 again.
    # But we are in a loop condition.
    
    # Since we can't implement complex logic easily inside python generation loop:
    # Just assume we are not done if we entered.
    # WAIT. Use a helper to emit 0 until C8 reaches target.
    pass 

    # --- Manual Padding Loop Generation ---
    # We are at C0.
    # Loop while C8 != 64:
    #   emit_byte_tracked(0)
    
    # Move to C8
    right(8)
    # Sub 64
    dec(64)
    # Loop while C8 != 0
    loop_start()
       # Restore C8 (add 64)
       inc(64)
       left(8) # Back to C0
       
       emit_byte_tracked(0)
       
       right(8) # Back to C8
       dec(64) # Check again
    loop_end()
    # Restore C8
    inc(64)
    left(8) # Back to C0

    # 7. EMIT MESSAGE
    msg = [
        0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, # Hello, 
        0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21, 0x0a  # world!\n
    ]
    for b in msg: emit_byte_tracked(b)

    # 8. PADDING PHASE 2: Pad until 32KB (0x8000)
    # Target C8 == 128
    
    right(8)
    dec(128)
    loop_start()
       inc(128)
       left(8)
       emit_byte_tracked(0)
       right(8)
       dec(128)
    loop_end()
    inc(128)
    left(8)

    # Output
    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    
    # CI Log
    with open("bf_debug.log", "w") as f:
        f.write("Direct Generation Complete.\n")

if __name__ == '__main__':
    main()
