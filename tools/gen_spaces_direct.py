#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: Fixed infinite loop by implementing a simple "Destructive Subtraction" state machine.
#      Garbage characters now correctly trigger a re-read of the input.

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
    # C0: Input
    # C1: Scratch/Copy
    # C2: Loop Flag (1=Run)
    # C3: Temp for Copy
    # C4: EOF Flag
    # C5: Token Result (0=S, 1=F)
    # C6: Opcode Acc

    def emit_read_token_logic():
        # Clear Flags
        right(4); clear(); left(4) # C4
        right(5); clear(); left(5) # C5
        
        # Start Search Loop (C2=1)
        right(2); clear(); inc(); loop_start()
        
        # Read Char to C0 (overwrite previous garbage)
        left(2); inp()
        
        # --- Check EOF (0) ---
        # Copy C0 -> C1 (using C3)
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end() # Move C0->C1,C3
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3) # Restore C0 from C3
        
        # If C1 == 0: EOF found
        right(); inc() # C1=1. If it was 0, now 1. If it was >0, now >1.
        # Check if C1==1. (It was 0)
        # Use C3 as flag "Was Zero" (Start 1)
        right(2); clear(); inc(); left(2) # C3=1
        
        dec() # C1--. Now 0 if it was 0.
        loop_start(); right(2); clear(); left(2); clear(); loop_end() # If C1!=0, Clear C3, Clear C1
        
        # If C3==1 (EOF Found)
        right(2); loop_start()
        clear()
        right(); inc() # C4=1
        left(2); dec() # C2=0 (Break)
        right()
        loop_end(); left(3) # Back to C0
        
        # --- Check S (32) ---
        # Run only if C2==1
        right(2); loop_start(); left(2) # If C2 check wrapper
        
        # Copy C0 -> C1
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        
        # C1 -= 32
        right(); dec(32)
        
        # If C1 == 0: S Found
        right(2); clear(); inc(); left(2) # C3=1
        loop_start(); right(2); clear(); left(2); clear(); loop_end()
        
        # If C3==1 (S Found)
        right(2); loop_start()
        clear()
        # C5=0. Break C2.
        left(); dec(); right()
        loop_end(); left(3)
        
        # End C2 Check
        right(2); loop_end(); left(2)


        # --- Check F (227) ---
        # Run only if C2==1
        right(2); loop_start(); left(2)
        
        # Copy C0 -> C1
        right(3); clear(); left(3)
        loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
        right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)
        
        # C1 -= 227
        right(); dec(227)
        
        # If C1 == 0: F Found
        right(2); clear(); inc(); left(2) # C3=1
        loop_start(); right(2); clear(); left(2); clear(); loop_end()
        
        # If C3==1 (F Found)
        right(2); loop_start()
        clear()
        # C5=1. Eat 2 chars. Break C2.
        right(2); inc(); left(2) # C5=1
        left(3); inp(); inp(); right(3)
        left(); dec(); right()
        loop_end(); left(3)
        
        # End C2 Check
        right(2); loop_end(); left(2)
        
        # End Search Loop (C2)
        # If no match (garbage), C2 is still 1, loop repeats, C0 gets new char.
        right(2); loop_end(); left(2)

    # 5. MAIN LOOP
    right(6); clear(); left(6)
    
    # Outer Loop C2=1
    right(2); clear(); inc(); loop_start(); left(2)
    
    right(6); clear(); left(6)
    
    emit_read_token_logic()
    # Check EOF C4
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    # Add to Acc
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
