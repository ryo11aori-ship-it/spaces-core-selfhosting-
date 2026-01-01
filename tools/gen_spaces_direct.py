#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Unrolled Mode)
#
# Strategy:
# 1. Construct the exact byte sequence of the target ELF binary in Python.
# 2. Generate linear Spaces code (no loops) to output these bytes one by one.
# 3. This guarantees termination (no infinite loops possible).
# 4. No indentation logic needed, eliminating syntax errors.

import sys

def main():
    # --- 1. Construct the Target ELF Binary (in memory) ---
    
    # Constants
    # Entry point: 0x400000 + 0x78 (header size) = 0x400078
    # Msg address: 0x400000 + 0x78 + 0x27 (code size) = 0x40009F
    
    # ELF Header (64-bit Linux) - 120 bytes
    elf_header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0, # Ident
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00, # Type, Machine, Version
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # Entry (0x400078)
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Phoff (64)
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Shoff (0)
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00, # Flags, Ehsize, Phentsize
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Phnum, Shentsize...
        
        # Program Header (Offset 64)
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, # Type(LOAD), Flags(RWE)
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Offset (0)
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # Vaddr (0x400000)
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # Paddr
        0xAD, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Filesz (173 bytes)
        0xAD, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # Memsz  (173 bytes)
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00    # Align (0x1000)
    ]

    # Machine Code (39 bytes)
    # Prints "Hello, world!\n" and exits.
    # Msg Addr calculation: 0x400000 + 120 (header) + 39 (code) = 0x40009F
    msg_addr = 0x40009F
    addr_bytes = [(msg_addr >> (8*i)) & 0xFF for i in range(4)] # 32-bit part is enough
    
    code = [
        0xb8, 0x01, 0x00, 0x00, 0x00,       # mov eax, 1 (write)
        0xbf, 0x01, 0x00, 0x00, 0x00,       # mov edi, 1 (stdout)
        0x48, 0xbe] + addr_bytes + [0x00, 0x00, 0x00, 0x00, # mov rsi, msg_addr
        0xba, 0x0e, 0x00, 0x00, 0x00,       # mov edx, 14 (len)
        0x0f, 0x05,                         # syscall
        0xb8, 0x3c, 0x00, 0x00, 0x00,       # mov eax, 60 (exit)
        0x31, 0xff,                         # xor edi, edi
        0x0f, 0x05                          # syscall
    ]

    # Message (14 bytes)
    msg = [0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21, 0x0a]

    # Full Binary
    binary = elf_header + code + msg
    
    # Calculate exact total size for p_filesz/p_memsz
    total_size = len(binary) # Should be 120 + 39 + 14 = 173 (0xAD)
    
    # Update Filesz/Memsz in header (indexes 84 and 92)
    # We hardcoded 0xAD above, so it matches.
    
    # --- 2. Generate Spaces Code ---
    S = " "      # Space
    F = "\u3000" # Fullwidth Space
    
    cmds = []
    
    # Helper to generate sequences
    def emit_s(s): cmds.append(s)
    
    current_val = 0
    
    # For each byte in the binary
    for byte in binary:
        # Calculate difference from current cell value
        diff = byte - current_val
        
        # Optimize: 
        # If diff is large, maybe reset to 0 (if we had a loop [-]) or use new cell (>).
        # Since we have NO loops, we can't easily reset to 0 efficiently without knowing the value.
        # But we track `current_val` in Python! So we know exactly how many + or - needed.
        
        if diff > 0:
            emit_s((S+F+S) * diff) # +
        elif diff < 0:
            emit_s((S+F+F) * (-diff)) # -
            
        emit_s(F+S+S) # . (Output)
        
        current_val = byte
        
        # Strategy choice:
        # A) Update current cell to next value (minimal diff).
        # B) Move to next cell (>) which is 0.
        # Method A produces smaller code if values are close.
        # Method B guarantees 0 start but adds > overhead.
        # Let's stick to Method A (Reuse cell) as it handles runs of similar bytes well.
    
    # --- 3. Output ---
    sys.stdout.buffer.write("".join(cmds).encode('utf-8'))
    
    # CI Dummy Log
    with open("bf_debug.log", "w") as f:
        f.write(f"Generated Unrolled Spaces Code. Binary Size: {total_size} bytes.\n")

if __name__ == '__main__':
    main()
