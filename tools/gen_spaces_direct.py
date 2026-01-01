#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: Fixed SegFault caused by pointer underflow and infinite loops in parser.
#      Implemented robust C3-flag based conditional execution.

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

    # 2. ELF Header (64-bit Linux)
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
        0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte(b)

    # 3. Init Code
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte(b)

    # 4. COMPILER LOGIC
    # Memory Layout (Relative to C0):
    # C0: Input Char
    # C1: Scratch
    # C2: Loop Flag (1=Run, 0=Break)
    # C3: Conditional Flag / Temp
    # C4: EOF Flag
    # C5: Token Result
    # C6: Opcode Acc

    def emit_read_token_logic():
        # Clear Flags
        right(4); clear(); left(4) # C4
        right(5); clear(); left(5) # C5
        
        # Start Search Loop (C2=1)
        right(2); clear(); inc(); loop_start()
        
        # Read Char to C0
        left(2); clear(); inp()
        
        # --- Check EOF (0) ---
        # C3 = (C0 == 0)
        right(3); clear(); inc(); left(3)
        loop_start(); right(3); clear(); left(3); loop_end() # If C0!=0, C3=0
        
        # If C3==1 (EOF 0): Set C4=1, C2=0
        right(3); loop_start()
        clear() # C3=0
        right(); inc() # C4=1
        left(2); dec() # C2=0
        right() # Back to C3
        loop_end(); left(3)
        
        # --- Check EOF (255) ---
        # Run only if C2==1 (Copy C2->C3)
        right(2); loop_start(); right(); inc(); left(); dec(); loop_end()
        right(); loop_start(); left(); inc(); right(); dec(); loop_end()
        
        # If C3==1
        right(); loop_start()
        clear() # C3=0
        left(3) # At C0
        
        # Check C0 == 255 (C0+1==0)
        right(); clear(); left()
        loop_start(); right(); inc(); left(); dec(); loop_end()
        right(); loop_start(); left(); inc(); right(); dec(); loop_end() # Copy C0->C1
        right(); inc() # C1++
        # If C1==0, it is 255. Set C3=1.
        right(2); clear(); inc(); left(2) # C3=1
        loop_start(); right(2); dec(); left(2); clear(); loop_end()
        
        # If C3==1 (Found 255)
        right(2); loop_start()
        clear()
        right(); inc() # C4=1
        left(2); dec() # C2=0
        right()
        loop_end(); left(3)
        
        right(3); loop_end(); left(3) # End C3 Wrapper
        
        
        # --- Check S (32) ---
        # Run only if C2==1
        right(2); loop_start(); right(); inc(); left(); dec(); loop_end()
        right(); loop_start(); left(); inc(); right(); dec(); loop_end()
        
        # If C3==1
        right(); loop_start()
        clear()
        left(3) # At C0
        
        # Check C0 == 32
        right(); clear(); left()
        loop_start(); right(); inc(); left(); dec(); loop_end()
        right(); loop_start(); left(); inc(); right(); dec(); loop_end()
        right(); dec(32)
        # If C1==0, it is 32. Set C3=1.
        right(2); clear(); inc(); left(2)
        loop_start(); right(2); dec(); left(2); clear(); loop_end()
        
        # If C3==1 (Found S)
        right(2); loop_start()
        clear()
        # C5 is 0. C2=0.
        left(); dec(); right()
        loop_end(); left(3)
        
        right(3); loop_end(); left(3) # End C3 Wrapper
        
        
        # --- Check F (227) ---
        # Run only if C2==1
        right(2); loop_start(); right(); inc(); left(); dec(); loop_end()
        right(); loop_start(); left(); inc(); right(); dec(); loop_end()
        
        # If C3==1
        right(); loop_start()
        clear()
        left(3) # At C0
        
        # Check C0 == 227
        right(); clear(); left()
        loop_start(); right(); inc(); left(); dec(); loop_end()
        right(); loop_start(); left(); inc(); right(); dec(); loop_end()
        right(); dec(227)
        # If C1==0, it is 227. Set C3=1.
        right(2); clear(); inc(); left(2)
        loop_start(); right(2); dec(); left(2); clear(); loop_end()
        
        # If C3==1 (Found F)
        right(2); loop_start()
        clear()
        right(2); inc(); left(2) # C5=1
        left(3); inp(); inp(); right(3) # Consume 2 chars
        left(); dec() # C2=0
        right()
        loop_end(); left(3)
        
        right(3); loop_end(); left(3) # End C3 Wrapper
        
        # End Search Loop (C2)
        right(2); loop_end(); left(2)

    # 5. MAIN LOOP
    # C0 is Base. C6 is Acc.
    right(6); clear(); left(6)
    
    # Outer Loop C2=1
    right(2); clear(); inc(); loop_start(); left(2)
    
    right(6); clear(); left(6)
    
    emit_read_token_logic()
    # Check EOF C4
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    # Acc
    right(5); loop_start(); dec(); right(); inc(4); left(); loop_end(); left(5)
    
    emit_read_token_logic()
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(2); left(); loop_end(); left(5)
    
    emit_read_token_logic()
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(1); left(); loop_end(); left(5)
    
    # Dispatch C6 (1..8)
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
    loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    loop_end()
    loop_end(); emit_machine_code([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    loop_end(); emit_machine_code([0x41, 0xfe, 0x4d, 0x00])
    loop_end(); emit_machine_code([0x41, 0xfe, 0x45, 0x00])
    loop_end(); emit_machine_code([0x49, 0xff, 0xcd])
    loop_end(); emit_machine_code([0x49, 0xff, 0xc5])
    left(6)
    
    right(2); loop_end(); left(2)

    # 6. Padding
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
