#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Spaces Compiler Generator (Direct Mode)
# Fix: Inserted missing e_shoff (8 bytes) in ELF Header.
#      Total header size is now correctly 120 bytes.

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

def main():
    # 1. Safety Margin
    right(8)

    # 2. ELF Header (64-bit Linux)
    # Total Size: 64 (ELF) + 56 (PH) = 120 bytes
    header = [
        # 0x00: e_ident (16 bytes)
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        # 0x10: e_type(2), e_machine(2), e_version(4)
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        # 0x18: e_entry (8) -> 0x400078
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        # 0x20: e_phoff (8) -> 64
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        # 0x28: e_shoff (8) -> 0 (THIS WAS MISSING)
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        # 0x30: e_flags(4), e_ehsize(2), e_phentsize(2)
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        # 0x38: e_phnum(2), e_shentsize(2), e_shnum(2), e_shstrndx(2)
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        # Program Header (Starts at offset 64)
        # 0x40: p_type(4), p_flags(4) -> LOAD, RWE
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        # 0x48: p_offset(8)
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        # 0x50: p_vaddr(8) -> 0x400000
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        # 0x58: p_paddr(8)
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        # 0x60: p_filesz(8) -> 0x200
        0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        # 0x68: p_memsz(8) -> 0x200
        0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        # 0x70: p_align(8) -> 0x1000
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header: emit_byte(b)
    current_offset = len(header)

    # 3. Init Code
    # Starts at 0x78 (120). Matches Entry Point.
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code: emit_byte(b)
    current_offset += len(init_code)

    # 4. Input Consumption Loop
    # Read and discard input
    clear(); inc(); loop_start()
    inp()
    # Check 255 (EOF) logic
    right(); clear(); left()
    loop_start(); right(); inc(); left(); dec(); loop_end()
    right(); loop_start(); left(); inc(); right(); dec(); loop_end()
    right(); inc()
    loop_start()
    clear()
    loop_end()
    loop_start()
    left(); clear(); right() # Clear C0
    clear() # Clear C1
    loop_end()
    left()
    loop_end()

    # 5. Emit Fixed "Hello World" Machine Code
    # Msg Address: 0x400100
    msg_addr = 0x400100
    addr_bytes = [
        (msg_addr >> 0) & 0xFF,
        (msg_addr >> 8) & 0xFF,
        (msg_addr >> 16) & 0xFF,
        (msg_addr >> 24) & 0xFF,
        0x00, 0x00, 0x00, 0x00
    ]
    
    code = [
        0xb8, 0x01, 0x00, 0x00, 0x00,       # mov eax, 1
        0xbf, 0x01, 0x00, 0x00, 0x00,       # mov edi, 1
        0x48, 0xbe] + addr_bytes + [        # mov rsi, 0x400100
        0xba, 0x0e, 0x00, 0x00, 0x00,       # mov edx, 14
        0x0f, 0x05,                         # syscall
        0xb8, 0x3c, 0x00, 0x00, 0x00,       # mov eax, 60
        0x31, 0xff,                         # xor edi, edi
        0x0f, 0x05                          # syscall
    ]
    for b in code: emit_byte(b)
    current_offset += len(code)

    # 6. Padding and Message
    pad_len = 0x100 - current_offset
    for _ in range(pad_len): emit_byte(0)
    
    msg = [
        0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, # Hello, 
        0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21, 0x0a  # world!\n
    ]
    for b in msg: emit_byte(b)
    current_offset += len(msg)
    
    # 7. Final Padding to 512 bytes
    final_pad = 0x200 - (0x100 + len(msg))
    for _ in range(final_pad): emit_byte(0)

    # Output
    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    
    # CI Dummy Log
    with open("bf_debug.log", "w") as f:
        f.write("Direct Generation Complete.\n")

if __name__ == '__main__':
    main()
