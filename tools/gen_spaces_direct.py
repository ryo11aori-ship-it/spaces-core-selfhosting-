#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: Robust Token Reader (loops until valid token) to prevent infinite loops.
# Fix: Strictly FLAT indentation to prevent Python errors.

import sys

# --- Constants ---
S = " "      # Space (0x20)
F = "\u3000" # Fullwidth Space (0xE3 0x80 0x80)
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
        0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Filesize 512
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # Memsize 131KB
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte(b)

    # 3. Init Code
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte(b)

    # 4. COMPILER LOGIC
    # C0: Input
    # C1: Scratch
    # C2: Loop Flag
    # C3: Check Flag
    # C4: EOF Flag (1=EOF)
    # C5: Token Result (0=S, 1=F)
    # C6: Opcode Accumulator

    # Define READ_TOKEN logic (Inline)
    # Loops until it finds S, F, or EOF.
    # Result in C5. EOF in C4.

    def read_token_inline():
        # Clear EOF Flag (C4)
        right(4); clear(); left(4)
        # Clear Result (C5)
        right(5); clear(); left(5)
        
        # Start Search Loop (C2 = 1)
        right(2); clear(); inc(); loop_start()
        
        # Read Char to C0
        left(2); clear(); inp()
        
        # --- Check EOF (0) ---
        # Logic: Copy C0->C3. If C3!=0, EOF_Check=0.
        right(3); clear(); left(3)
        # Copy C0 -> C3 using C1
        right(); clear(); left()
        loop_start(); right(); inc(); right(2); inc(); left(3); dec(); loop_end()
        right(3); loop_start(); left(3); inc(); right(3); dec(); loop_end()
        left(3)
        # If C3 is non-zero, it's NOT EOF(0).
        # Set C1=1 (EOF Found). If C3!=0, Set C1=0.
        right(); clear(); inc() # C1=1
        right(2)
        loop_start()
        left(2); clear() # C1=0
        right(2); clear() # C3=0
        loop_end()
        left(3)
        
        # If C1 is 1 (EOF found)
        right()
        loop_start()
        clear() # Clear C1
        # Set EOF Flag C4=1
        right(3); inc(); left(3)
        # Break Search Loop (C2)
        right(); dec(); left()
        loop_end()
        left()
        
        # --- Check EOF (255) ---
        # If C2 is still 1.
        right(2)
        loop_start()
        left(2)
        
        # Check if C0 == 255. (C0+1 == 0 in 8-bit)
        # Copy C0->C3
        right(3); clear(); left(3)
        right(); clear(); left()
        loop_start(); right(); inc(); right(2); inc(); left(3); dec(); loop_end()
        right(3); loop_start(); left(3); inc(); right(3); dec(); loop_end()
        # Increment C3
        inc()
        # If C3!=0, Not 255.
        # Set C1=1 (EOF Found). If C3!=0, C1=0.
        left(2); right(); clear(); inc(); right(2)
        loop_start()
        left(2); clear() # C1=0
        right(2); clear() # C3=0
        loop_end()
        left(3)
        
        # If C1 is 1 (EOF found)
        right()
        loop_start()
        clear()
        right(3); inc(); left(3) # C4=1
        right(); dec(); left()   # Break C2
        loop_end()
        left()
        
        # End C2 Wrapper
        right(2); loop_end(); left(2)


        # --- Check S (32) ---
        # If C2 is still 1
        right(2); loop_start(); left(2)
        
        # Copy C0->C3
        right(3); clear(); left(3)
        right(); clear(); left()
        loop_start(); right(); inc(); right(2); inc(); left(3); dec(); loop_end()
        right(3); loop_start(); left(3); inc(); right(3); dec(); loop_end()
        
        # Subtract 32 from C3
        dec(32)
        
        # If C3==0, Found S.
        # Set C1=1 (Found S). If C3!=0, C1=0.
        left(2); right(); clear(); inc(); right(2)
        loop_start()
        left(2); clear() # C1=0
        right(2); clear() # C3=0
        loop_end()
        left(3)
        
        # If C1=1 (Found S)
        right()
        loop_start()
        clear()
        # C5 is already 0 (S).
        # Break C2
        right(); dec(); left()
        loop_end()
        left()
        
        # End C2 Wrapper
        right(2); loop_end(); left(2)
        
        
        # --- Check F (227) ---
        # If C2 is still 1
        right(2); loop_start(); left(2)
        
        # Copy C0->C3
        right(3); clear(); left(3)
        right(); clear(); left()
        loop_start(); right(); inc(); right(2); inc(); left(3); dec(); loop_end()
        right(3); loop_start(); left(3); inc(); right(3); dec(); loop_end()
        
        # Subtract 227 from C3
        dec(227)
        
        # If C3==0, Found F.
        left(2); right(); clear(); inc(); right(2)
        loop_start()
        left(2); clear() # C1=0
        right(2); clear() # C3=0
        loop_end()
        left(3)
        
        # If C1=1 (Found F)
        right()
        loop_start()
        clear()
        # Set C5=1 (F)
        right(4); inc(); left(4)
        # Consume 2 bytes
        left(); inp(); inp(); right()
        # Break C2
        right(); dec(); left()
        loop_end()
        left()
        
        # End C2 Wrapper
        right(2); loop_end(); left(2)
        
        # End Search Loop (C2)
        # If no match (garbage), C2 is still 1, loop continues.
        right(2); loop_end(); left(2)

    # Main Compiler Loop
    right(6); clear(); left(6)
    
    # Outer Loop (Infinite until break)
    right(2); clear(); inc(); loop_start(); left(2)
    
    # Clear Acc C6
    right(6); clear(); left(6)
    
    # --- Bit 1 (Weight 4) ---
    read_token_inline()
    # Check EOF (C4)
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    # Add C5*4 to C6
    right(5); loop_start(); dec(); right(); inc(4); left(); loop_end(); left(5)
    
    # --- Bit 2 (Weight 2) ---
    read_token_inline()
    # Check EOF (C4) - If EOF mid-stream, we break too
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(2); left(); loop_end(); left(5)
    
    # --- Bit 3 (Weight 1) ---
    read_token_inline()
    # Check EOF (C4)
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(1); left(); loop_end(); left(5)
    
    # --- Dispatch C6 ---
    # To check C6 without destroying it, copy to C3?
    # No, C6 is accumulator, we can destroy it if we handle it.
    
    # Simple Decrement Dispatch
    # C6 is 0..7.
    # Add 1 to C6 to make it 1..8. 0 was >.
    right(6); inc()
    
    loop_start() # Case 1: > (0)
    dec(); loop_start() # Case 2: < (1)
    dec(); loop_start() # Case 3: + (2)
    dec(); loop_start() # Case 4: - (3)
    dec(); loop_start() # Case 5: . (4)
    dec(); loop_start() # Case 6: , (5)
    dec(); loop_start() # Case 7: [ (6)
    dec(); loop_start() # Case 8: ] (7)
    clear() # >8 Invalid
    loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    loop_end() # Input , ignored
    loop_end(); emit_machine_code([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    loop_end(); emit_machine_code([0x41, 0xfe, 0x4d, 0x00])
    loop_end(); emit_machine_code([0x41, 0xfe, 0x45, 0x00])
    loop_end(); emit_machine_code([0x49, 0xff, 0xcd])
    loop_end(); emit_machine_code([0x49, 0xff, 0xc5])
    
    left(6) # Back to C0
    
    # Loop back (C2 is still 1 unless EOF cleared it)
    right(2); loop_end(); left(2)

    # Padding
    right(8); clear(); inc(255); loop_start()
    right(); clear(); inc(255); loop_start()
    right(); out(); left(); dec()
    loop_end(); left(); dec()
    loop_end()

    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    
    with open("bf_debug.log", "w") as f:
        f.write("Direct Generation Complete.\n")

if __name__ == '__main__':
    main()
