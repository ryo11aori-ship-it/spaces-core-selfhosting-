#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: Fixed infinite loop by implementing robust Token Reader (Skip garbage/newline).

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
    # Filesize: 0x200 (512), Memsize: 0x20000 (131KB)
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
        0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte(b)

    # 3. Init Code
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte(b)

    # 4. COMPILER LOGIC
    # C0: Input Char
    # C1: Temp / Copy
    # C2: Search Loop Flag
    # C3: Check Flag
    # C4: EOF Flag
    # C5: Token Result (0=S, 1=F)
    # C6: Opcode Acc

    def read_token():
        # Reset Flags
        right(4); clear(); left(4) # Clear EOF Flag C4
        right(5); clear(); left(5) # Clear Token Result C5
        
        # Start Search Loop (C2 = 1)
        right(2); clear(); inc(); loop_start()
        
        # Read Char to C0
        left(2); clear(); inp()
        
        # --- Check EOF (0) ---
        # Logic: C3=1. If C0!=0 then C3=0.
        right(3); clear(); inc(); left(3) # C3=1
        
        # Copy C0->C1 to check non-zero
        right(); clear(); left()
        loop_start(); right(); inc(); left(); dec(); loop_end() # Move C0->C1
        right(); loop_start(); left(); inc(); right(); dec(); loop_end(); left() # Restore C0 from C1
        
        # If C1 (Copy of C0) is non-zero, set C3=0
        right()
        loop_start()
            right(2); dec(); left(2) # C3=0
            clear() # Clear C1
        loop_end()
        left()
        
        # If C3 is 1 (EOF), Handle Exit
        right(3)
        loop_start()
            # Set EOF Flag C4=1
            right(); inc(); left()
            # Break Search Loop C2=0
            left(); dec(); right()
            # Clear C3
            clear()
        loop_end()
        left(3)
        
        # --- If Not EOF (C2 is still 1), Check Chars ---
        left() # Go to C2
        loop_start() # If C2==1
            left(2) # Go to C0
            
            # Check S (32)
            # Copy C0->C1
            right(); clear(); left()
            loop_start(); right(); inc(); left(); dec(); loop_end()
            right(); loop_start(); left(); inc(); right(); dec(); loop_end()
            
            # C1 -= 32
            right(); dec(32)
            
            # Check if C1 == 0
            # Set C3=1. If C1!=0, C3=0.
            right(2); clear(); inc(); left(2) # C3=1
            loop_start(); right(2); dec(); left(2); clear(); loop_end() # If C1!=0, C3=0, Clear C1
            
            # If C3==1 (It was S)
            right(2)
            loop_start()
                 # Found S! C5 is already 0.
                 # Break Search Loop C2=0
                 left(); dec(); right()
                 clear() # Clear C3
            loop_end()
            left(2)
            
            # If C2 is still 1 (Not S), Check F (227)
            # We must re-check C0 (it is preserved).
            # But wait, we can just check if C0 == 227.
            
            # Go to C2
            left() # C1
            loop_start() # If C2==1 (Not S yet)
                left() # C0
                
                # Copy C0->C1
                right(); clear(); left()
                loop_start(); right(); inc(); left(); dec(); loop_end()
                right(); loop_start(); left(); inc(); right(); dec(); loop_end()
                
                # C1 -= 227
                right(); dec(227)
                
                # Check if C1 == 0
                right(2); clear(); inc(); left(2) # C3=1
                loop_start(); right(2); dec(); left(2); clear(); loop_end()
                
                # If C3==1 (It was F)
                right(2)
                loop_start()
                    # Found F! Set C5=1
                    right(2); inc(); left(2)
                    # Consume 2 bytes
                    left(3); inp(); inp(); right(3)
                    # Break Search Loop C2=0
                    left(); dec(); right()
                    clear()
                loop_end()
                left(2)
                
                # If C2 is still 1 (Not S, Not F) -> Garbage (Newline etc)
                # Just Loop again (C2 is still 1)
                
                # Break inner wrapper C1
                left()
                clear() # Clear C1 (Dummy)
                right()
            loop_end()
            
            # Break inner wrapper C2
            left() # C1
            clear() # Clear C1 (Dummy)
            right()
        loop_end()
        left(2) # Back to C0
        
        # End Search Loop (C2)
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
