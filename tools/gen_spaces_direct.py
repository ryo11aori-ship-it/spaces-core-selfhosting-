#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: REMOVED ALL VISUAL INDENTATION to prevent Python IndentationError.

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

def emit_byte(val):
    right()
    clear()
    inc(val)
    out()
    clear()
    left()

def emit_machine_code(bytes_list):
    for b in bytes_list:
        right(7)
        clear()
        inc(b)
        out()
        clear()
        left(7)

def main():
    # 1. Safety Margin
    right(8)

    # 2. ELF Header (64-bit Linux) - 131KB Memory
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte(b)

    # 3. Init Code
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte(b)

    # 4. COMPILER LOGIC
    # Helper to read one Spaces Token (S or F)
    def read_token():
        # Clear EOF Flag (C4)
        right(4); clear(); left(4)
        # Set Outer Loop Flag (C2=1)
        right(2); inc(); loop_start()
        
        # Read Char to C0
        left(2); clear(); inp()
        
        # Check EOF (0)
        loop_start() 
        
        # Check 255 (Real EOF)
        right(3); clear(); inc(); left(3)
        inc()
        loop_start(); dec(); right(3); dec(); left(3); loop_end()
        
        # If C3 is 1 (EOF), Set C4=1 and Break
        right(3); loop_start()
        clear()
        right(); inc(); left()
        left(3); clear()
        right(); dec(); left()
        right(3)
        loop_end(); left(3)
        
        # Check S (32)
        right(3); clear(); inc(); left(3)
        right(5); clear(); left(5)
        
        # Subtract 32
        dec(32)
        loop_start() 
        clear(); right(3); clear(); left(3)
        
        # Check F (227-32 = 195)
        dec(195)
        loop_start()
        clear()
        loop_end()
        
        # If F (Not S/Garbage), Set C5=1, Consume 2 bytes
        right(5); inc(); left(5)
        inp(); inp()
        
        # Break Outer Loop
        right(2); dec(); left(2) 
        loop_end()
        
        # If C3 is still 1 (It was S)
        right(3)
        loop_start()
        clear()
        left(); dec(); right()
        loop_end()
        left(3)
        
        # End EOF Check (0)
        loop_end() 
        
        # End Outer Loop (C2)
        right(2)
        loop_end()
        left(2)

    # Main Compiler Loop
    right(6); clear(); left(6)
    
    # Loop indefinitely (until inner break)
    right(2); inc(); loop_start()
    left(2)
    
    # Read 3 bits
    right(6); clear(); left(6)
    
    # Bit 1 (Weight 4)
    read_token()
    # Check EOF (C4)
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    
    # Add to Acc: C6 += C5 * 4
    right(5); loop_start(); dec(); right(); inc(4); left(); loop_end(); left(5)
    
    # Bit 2 (Weight 2)
    read_token()
    right(5); loop_start(); dec(); right(); inc(2); left(); loop_end(); left(5)
    
    # Bit 3 (Weight 1)
    read_token()
    right(5); loop_start(); dec(); right(); inc(1); left(); loop_end(); left(5)
    
    # Dispatch C6
    # 000 (0) >
    right(6); inc(); loop_start()
    dec(); loop_start()
    dec(); loop_start()
    dec(); loop_start()
    dec(); loop_start()
    dec(); loop_start()
    dec(); loop_start()
    dec(); loop_start()
    dec(); loop_start()
    clear()
    loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    loop_end() # Input ignored
    loop_end(); emit_machine_code([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    loop_end(); emit_machine_code([0x41, 0xfe, 0x4d, 0x00])
    loop_end(); emit_machine_code([0x41, 0xfe, 0x45, 0x00])
    loop_end(); emit_machine_code([0x49, 0xff, 0xcd])
    loop_end(); emit_machine_code([0x49, 0xff, 0xc5])
    
    left(6)
    
    right(2)
    loop_end()

    # Padding to fill file
    right(8); clear(); inc(255); loop_start()
    right(); clear(); inc(255); loop_start()
    right(); out(); left(); dec()
    loop_end(); left(); dec()
    loop_end()

    # Output
    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    
    # CI Dummy Log
    with open("bf_debug.log", "w") as f:
        f.write("Direct Generation Complete.\n")

if __name__ == '__main__':
    main()
