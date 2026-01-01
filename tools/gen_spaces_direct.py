#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Features:
# 1. Output Valid ELF Header (Corrected 120 bytes structure)
# 2. Large Memory Allocation (p_memsz = 0x20000) for Brainfuck Tape
# 3. Real Parser Logic: Reads S/F tokens and emits corresponding x64 instructions.
# 4. Flat Indentation: No Python IndentationError.

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
    # Header Size: 120 bytes.
    # We need p_memsz to be large enough for the BF tape (e.g. 0x20000 = 131KB).
    # Previous Exec format error was due to shifted offsets, not the size itself.
    header = [
        # Ident (16)
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        # Type, Machine, Version
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        # Entry (0x400078)
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        # Phoff (64)
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        # Shoff (0) - Corrected
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        # Flags, Ehsize, Phentsize
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        # Phnum, Shentsize, Shnum, Shstrndx
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        # Program Header (Offset 64)
        # Type(LOAD), Flags(RWE)
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        # Offset
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        # Vaddr (0x400000)
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        # Paddr
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        # Filesz (0x10000 = 64KB just to be safe and cover code)
        0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
        # Memsz (0x20000 = 131KB for Tape)
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
        # Align (0x1000)
        0x00, 10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte(b)

    # 3. Init Code
    # mov r13, 0x408000 (Start of BF Tape, well inside Memsz)
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte(b)

    # 4. PARSER LOGIC
    # Defines how to read S/F tokens from input and ignore garbage/newlines.
    
    # Python Function to emit "Read One Token" logic
    # Result: C5 (0=S, 1=F). EOF: C4=1.
    def emit_read_token_logic():
        # Clear Flags
        right(4); clear(); left(4) # C4=0
        right(5); clear(); left(5) # C5=0
        
        # Loop until S or F or EOF found (C2=1)
        right(2); clear(); inc(); loop_start()
        
        # Read Char -> C0
        left(2); clear(); inp()
        
        # Check EOF (0)
        loop_start() # If C0 != 0
        
        # Check EOF (255)
        # Logic: C3=1. If C0+1==0, C3=1. Else C3=0.
        right(3); clear(); inc(); left(3) # C3=1
        inc() # C0++
        loop_start(); dec(); right(3); dec(); left(3); loop_end() # If C0!=0 -> C3=0
        # If C3==1 (It was 255), Set C4=1, Break.
        right(3); loop_start()
        clear(); right(); inc(); left(); left(3); clear(); right(); dec(); left(); right(3)
        loop_end(); left(3)
        
        # If C2 is still 1 (Not EOF)
        left(); loop_start(); left(2) # At C0
        
        # Check S (32). Note: C0 is already incremented! So check 33.
        # Restore C0
        dec() 
        
        # Copy C0 -> C3
        right(3); clear(); left(3); right(); clear(); left()
        loop_start(); right(); inc(); right(2); inc(); left(3); dec(); loop_end()
        right(); loop_start(); left(); inc(); right(); dec(); loop_end(); left()
        
        # Check if C3 == 32
        right(3); dec(32)
        # If C3==0, It is S.
        # Set C1=1 (Found S).
        left(2); right(); clear(); inc(); right(2)
        loop_start(); left(2); clear(); right(2); clear(); loop_end(); left(3)
        
        # If C1=1 (S Found)
        right()
        loop_start()
        clear()
        # C5 is 0 (S). Break C2.
        right(); dec(); left()
        loop_end()
        left()
        
        # Check F (227)
        # If C2 is still 1.
        right(); loop_start(); left(2)
        
        # Copy C0 -> C3
        right(3); clear(); left(3); right(); clear(); left()
        loop_start(); right(); inc(); right(2); inc(); left(3); dec(); loop_end()
        right(); loop_start(); left(); inc(); right(); dec(); loop_end(); left()
        
        # Check if C3 == 227
        right(3); dec(227)
        # If C3==0, It is F.
        left(2); right(); clear(); inc(); right(2)
        loop_start(); left(2); clear(); right(2); clear(); loop_end(); left(3)
        
        # If C1=1 (F Found)
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
        
        # End C2 Check (F)
        right(); loop_end(); left()
        
        # End C2 Check (S)
        right(); loop_end(); left()
        
        # End C2 Check (Not EOF)
        right(2); loop_end(); left(2)
        
        # End EOF Check (0)
        loop_end()
        
        # If C0 was 0, C2 loop runs once then exits? No, C0 is condition.
        # If C0 was 0, loop skipped. C4 needs to be set.
        # Actually if C0=0, we just need to detect it.
        # Use C4. C4 is 0. If C0=0, we are here.
        # If C0!=0, we processed.
        # This is complex.
        
        # Simpler: If C0=0, Set C4=1, Clear C2.
        # We need a flag "WasNonZero".
        # Let's assume input always ends with 0 or 255.
        
        # Loop back if C2==1 (Garbage was found, or C0=0 and we missed it?)
        # If C0=0, the inner loop didn't run. C2 is still 1.
        # We need to break C2 if C0=0.
        
        # Check C0
        right(3); clear(); inc(); left(3) # C3=1
        loop_start(); right(3); clear(); left(3); loop_end() # If C0!=0, C3=0
        
        # If C3=1 (C0 was 0), Set C4=1, Clear C2
        right(3); loop_start()
        clear(); right(); inc(); left(); left(); dec(); right(); right(3)
        loop_end(); left(3)
        
        # Loop End C2
        right(2); loop_end(); left(2)

    # 5. MAIN COMPILER LOOP
    
    # C0: Input, C6: Acc
    right(6); clear(); left(6)
    
    # Outer Loop (Infinite)
    right(2); clear(); inc(); loop_start(); left(2)
    
    # Clear Acc C6
    right(6); clear(); left(6)
    
    # Bit 1 (Weight 4)
    emit_read_token_logic()
    # Check EOF C4 -> Break Main Loop
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    # Add to Acc
    right(5); loop_start(); dec(); right(); inc(4); left(); loop_end(); left(5)
    
    # Bit 2 (Weight 2)
    emit_read_token_logic()
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(2); left(); loop_end(); left(5)
    
    # Bit 3 (Weight 1)
    emit_read_token_logic()
    right(4); loop_start(); clear(); left(2); dec(); right(2); loop_end(); left(4)
    right(5); loop_start(); dec(); right(); inc(1); left(); loop_end(); left(5)
    
    # Dispatch C6
    # 000(0)=>, 001(1)=< ...
    # Increment C6 to 1-8
    right(6); inc()
    
    loop_start() # Case 1: >
    dec(); loop_start() # Case 2: <
    dec(); loop_start() # Case 3: +
    dec(); loop_start() # Case 4: -
    dec(); loop_start() # Case 5: .
    dec(); loop_start() # Case 6: ,
    dec(); loop_start() # Case 7: [
    dec(); loop_start() # Case 8: ]
    clear()
    loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    loop_end(); emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    loop_end() # , ignored
    loop_end(); emit_machine_code([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    loop_end(); emit_machine_code([0x41, 0xfe, 0x4d, 0x00])
    loop_end(); emit_machine_code([0x41, 0xfe, 0x45, 0x00])
    loop_end(); emit_machine_code([0x49, 0xff, 0xcd])
    loop_end(); emit_machine_code([0x49, 0xff, 0xc5])
    
    left(6) # Back to C0
    
    # Main Loop End
    right(2); loop_end(); left(2)

    # 6. Padding
    # Fill remaining bytes with 0 up to Filesz (0x10000)
    # This is a bit large to do with loop...
    # Simple padding to ensure valid ELF size
    right(8); clear(); inc(255); loop_start()
    right(); clear(); inc(255); loop_start()
    right(); out(); left(); dec()
    loop_end(); left(); dec()
    loop_end()

    # Output
    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    
    # CI Log
    with open("bf_debug.log", "w") as f:
        f.write("Direct Generation Complete.\n")

if __name__ == '__main__':
    main()
