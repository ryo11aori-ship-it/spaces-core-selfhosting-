#!/usr/bin/env python3
import sys

# === Flat Helper Functions ===
S = " "
F = "\u3000"
def e(s): sys.stdout.write(s + "\n")
def R(n=1): 
    if n > 0: e((S + S + S) * n)
def L(n=1): 
    if n > 0: e((S + S + F) * n)
def I(n=1): 
    if n > 0: e((S + F + S) * n)
def D(n=1): 
    if n > 0: e((S + F + F) * n)
def O(): e(F + S + S)
def N(): e(F + S + F)
def B(): e(F + F + S)
def C(): e(F + F + F)
def Z(): B(); D(); C()

def emit_byte_to_buffer(val):
    Z()
    I(val)
    R(1)

def emit_bytes(vals):
    for v in vals:
        emit_byte_to_buffer(v)

def main():
    # Move to Buffer Start (300)
    R(300)
    
    # === 1. ELF Header (64 bytes) ===
    # \x7fELF...
    emit_bytes([0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0])
    # Type Exec(2), Machine x86-64(62), Version 1
    emit_bytes([0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00])
    # Entry Point 0x400078 (Header 120 bytes)
    emit_bytes([0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    # Phoff 64
    emit_bytes([0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # Shoff 0
    emit_bytes([0,0,0,0,0,0,0,0])
    # Flags, Ehsize(64), Phentsize(56), Phnum(1), Shentsize(64), Shnum(0), Shstrndx(0)
    emit_bytes([0,0,0,0, 64,0, 56,0, 1,0, 64,0, 0,0, 0,0])
    
    # === 2. Program Header (56 bytes) ===
    # Type Load(1), Flags RWE(7), Offset(0)
    emit_bytes([0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0,0,0,0,0,0,0,0])
    # Vaddr 0x400000
    emit_bytes([0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    # Paddr 0x400000
    emit_bytes([0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    # FileSize (167 bytes - enough for our payload)
    emit_bytes([0xa7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # MemSize
    emit_bytes([0xa7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # Align 0x1000
    emit_bytes([0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    # === 3. Code Init (7 bytes) ===
    # mov rbx, 0x402000 (Data Pointer)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    # === 4. Payload: Print 'A' and Exit (40 bytes) ===
    # mov rax, 1 (write)
    emit_bytes([0x48, 0xc7, 0xc0, 0x01, 0x00, 0x00, 0x00])
    # mov rdi, 1 (stdout)
    emit_bytes([0x48, 0xc7, 0xc7, 0x01, 0x00, 0x00, 0x00])
    # push 0x41 ('A')
    emit_bytes([0x6a, 0x41])
    # mov rsi, rsp
    emit_bytes([0x48, 0x89, 0xe6])
    # mov rdx, 1 (len)
    emit_bytes([0x48, 0xc7, 0xc2, 0x01, 0x00, 0x00, 0x00])
    # syscall
    emit_bytes([0x0f, 0x05])
    
    # mov rax, 60 (exit)
    emit_bytes([0x48, 0xc7, 0xc0, 0x3c, 0x00, 0x00, 0x00])
    # xor rdi, rdi
    emit_bytes([0x48, 0x31, 0xff])
    # syscall
    emit_bytes([0x0f, 0x05])
    
    # Total bytes emitted: 64 + 56 + 7 + 40 = 167 bytes.
    # Current Pointer: 300 + 167 = 467.
    
    # === 5. Output Loop ===
    # We want to print [300, 467).
    # Use Cell 299 as counter.
    # Move from 467 to 299.
    L(168)
    
    # Set Counter to 167
    I(167)
    
    # Loop
    B()
    R(1)
    O()
    L(1)
    D()
    C()

if __name__ == "__main__":
    main()
