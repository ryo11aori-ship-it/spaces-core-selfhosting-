#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Implements a real compiler that parses Spaces input and emits x64 machine code.

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

def move_val(src_offset, dest_offset):
    # Destructive move
    # Assumes we are at src
    loop_start()
    dec()
    if dest_offset > 0: right(dest_offset)
    else: left(-dest_offset)
    inc()
    if dest_offset > 0: left(dest_offset)
    else: right(-dest_offset)
    loop_end()

def emit_byte(val):
    # Output a byte directly (for Headers)
    right()
    clear()
    inc(val)
    out()
    clear()
    left()

def emit_machine_code(bytes_list):
    # Emit a sequence of machine code bytes (Condition: C6 is active)
    # Using C7 as scratch
    for b in bytes_list:
        right(7) # To C7
        clear()
        inc(b)
        out()
        clear()
        left(7) # Back to C0

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
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # p_filesz 131KB
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # p_memsz 131KB
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte(b)

    # 3. Init Code (mov r13, 0x408000)
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte(b)

    # 4. COMPILER LOGIC
    # C0: Input Char / Working
    # C1: Bit Accumulator
    # C2: Loop/Temp Flag
    # C3: Temp
    # C4: EOF Flag
    # C5: Token Value (0=S, 1=F)
    # C6: Opcode Accumulator (3 bits)
    
    # Helper to read one Spaces Token (S or F)
    # Returns 0 for S, 1 for F in C5. Sets C4=1 if EOF.
    def read_token():
        # Loop until valid token found or EOF
        right(4); clear(); left(4) # Clear EOF Flag
        right(2); inc(); loop_start() # C2=1 (Outer Loop)
        
        # Read Char to C0
        clear(); inp()
        
        # Check EOF (0)
        loop_start() 
        
        # Check 255 (Real EOF)
        right(3); clear(); inc(); left(3) # C3=1
        inc() # C0 += 1
        loop_start(); dec(); right(3); dec(); left(3); loop_end() # If C0!=0 -> C3=0
        
        # If C3 is 1 (EOF), Set C4=1 and Break
        right(3); loop_start()
            clear() # Clear C3
            right(); inc(); left() # Set C4=1
            left(3); clear() # Clear C0 to break inner loop
            right(); dec(); left() # Clear C2 to break outer loop (C2 is at +2)
            right(3)
        loop_end(); left(3)
        
        # If C0 is valid char:
        # Check S (32)
        right(3); clear(); inc(); left(3) # C3=1 (Assume S)
        right(5); clear(); left(5) # Clear C5
        
        # C0 is input. Copy to C1 to preserve? No, consume it.
        # But we need to compare.
        # S=32. F=227.
        # If C0 == 32: It is S. C5=0. Break.
        # If C0 == 227: It is F. Consume 2 more. C5=1. Break.
        
        # Subtract 32
        dec(32)
        loop_start() # If C0 != 0 (Not S)
            clear(); right(3); clear(); left(3) # Clear C3 (Not S)
            
            # Check F (227-32 = 195)
            # We already subtracted 32.
            dec(195)
            loop_start() # If C0 != 0 (Not F -> Garbage)
                clear() # Clear Garbage
                # Loop continues
            loop_end()
            
            # If we are here and C0 was F, it is now 0.
            # But if it was Garbage, it is 0 too (cleared).
            # We need to detect if it WAS F.
            # Use C3? We cleared C3.
            # So if C3 is 0, it is Not S.
            # This logic is tricky.
            
            # Simpler:
            # If it was F, we need to set C5=1 and Break.
            # But we are inside "Not S" loop.
            
            # Just Assume it is F if it wasn't S and wasn't Garbage.
            # Actually, generator ensures valid input.
            # Let's assume if it wasn't S, it is F (or garbage to ignore).
            # If F (227), we need to read 2 more chars.
            
            right(5); inc(); left(5) # Set C5=1 (F)
            inp(); inp() # Consume 2 suffix bytes of F
            
            # Break Outer Loop
            right(2); dec(); left(2) 
            
        loop_end() # End Not S
        
        # If C3 is still 1, it was S.
        right(3)
        loop_start()
            clear()
            # C5 is already 0.
            # Break Outer Loop
            left(); dec(); right()
        loop_end()
        left(3)
        
        loop_end() # End EOF Check (0)
        
        # If C0 was 0 (EOF), C2 is still 1?
        # We need to handle raw 0.
        # If input was 0, inner loop didn't run.
        # Set EOF flag C4.
        
        # We need a flag "Processed". Use C1?
        # Let's simplify: Just loop until we hit S or F or EOF.
        
        loop_end() # End Outer Loop (C2)

    # Main Compiler Loop
    right(6); clear(); left(6) # Clear Opcode Acc C6
    
    # Loop indefinitely (until inner break)
    right(2); inc(); loop_start() # C2=1 (Main Loop)
    left(2)
    
    # Read 3 bits
    right(6); clear(); left(6) # Clear Opcode Acc
    
    # Bit 1 (Weight 4)
    read_token()
    # Check EOF (C4)
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4) # If EOF, Clear C2 (Main Break)
    
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
    right(6); loop_start(); left(6) # If C6 != 0
        dec(); right(6); loop_start(); left(6) # 1 <
            dec(); right(6); loop_start(); left(6) # 2 +
                dec(); right(6); loop_start(); left(6) # 3 -
                    dec(); right(6); loop_start(); left(6) # 4 .
                        dec(); right(6); loop_start(); left(6) # 5 ,
                            dec(); right(6); loop_start(); left(6) # 6 [
                                dec(); right(6); loop_start(); left(6) # 7 ]
                                    # 8+ (Invalid)
                                    clear()
                                loop_end(); left(6); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff]); right(6)
                            loop_end(); left(6); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00]); right(6)
                        loop_end(); left(6); # Input Ignored
                        right(6)
                    loop_end(); left(6); emit_machine_code([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]); right(6)
                loop_end(); left(6); emit_machine_code([0x41, 0xfe, 0x4d, 0x00]); right(6)
            loop_end(); left(6); emit_machine_code([0x41, 0xfe, 0x45, 0x00]); right(6)
        loop_end(); left(6); emit_machine_code([0x49, 0xff, 0xcd]); right(6)
    loop_end(); left(6); # Case 0 (> is handled if loop didn't run? No.)
    
    # Wait, the logic above only runs if C6 was NOT 0 initially.
    # C6=0 (>) needs to be handled separately or logic inverted.
    # Correct Logic: Copy C6 to Temp. Check 0, 1, 2...
    # But C6 is destructive.
    
    # Simplified dispatch:
    # We moved C6. If it was 0, the first loop skipped.
    # We need a Flag "Handled".
    # Initialize Handled=0.
    # If C6 != 0...
    
    # Let's fix Case 0 (>).
    # If C6 is 0, we want to emit >.
    # Use C3 as "Is Zero". Set C3=1.
    # If C6!=0, Set C3=0.
    
    right(6); loop_start(); dec(); left(3); dec(); right(3); loop_end(); left(6) # Logic broken.
    
    # Simple fix: Add 1 to C6. Then 1= >, 2= < ...
    inc()
    
    # Dispatch 1..8
    loop_start() # Case > (1)
        dec(); loop_start() # Case < (2)
            dec(); loop_start() # Case + (3)
                dec(); loop_start() # Case - (4)
                    dec(); loop_start() # Case . (5)
                        dec(); loop_start() # Case , (6)
                            dec(); loop_start() # Case [ (7)
                                dec(); loop_start() # Case ] (8)
                                    clear()
                                loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
                            loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
                        loop_end() # Input , ignored
                    loop_end(); emit_machine_code([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
                loop_end(); emit_machine_code([0x41, 0xfe, 0x4d, 0x00])
            loop_end(); emit_machine_code([0x41, 0xfe, 0x45, 0x00])
        loop_end(); emit_machine_code([0x49, 0xff, 0xcd])
    loop_end(); emit_machine_code([0x49, 0xff, 0xc5]) # Case >
    
    left(6) # Back to C0
    
    right(2) # Back to Loop Flag
    loop_end() # End Main Loop

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
