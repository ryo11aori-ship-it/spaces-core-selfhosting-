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
    R(300)
    # ELF Header (167 bytes)
    emit_bytes([0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0])
    emit_bytes([0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00])
    emit_bytes([0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0,0,0,0,0,0,0,0])
    emit_bytes([0,0,0,0, 64,0, 56,0, 1,0, 64,0, 0,0, 0,0])
    emit_bytes([0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0,0,0,0,0,0,0,0])
    emit_bytes([0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    # Init Counter at Ptr+1
    R(1)
    I(167)
    L(1)
    
    # Read First Char to Ptr+2
    R(2)
    N()
    # EOF Fix
    I(1); B(); D(1); C()
    L(2)
    
    # Work Area Gap
    GAP = 1000
    
    # Loop while Char(Ptr+2) != 0
    R(2)
    B()
        L(2) # Back to Ptr
        # Move Char from Ptr+2 to Ptr+GAP
        R(2); Z(); I(1); L(1); B(); R(GAP-2); I(1); L(GAP-2); D(); C()
        R(GAP) # At Ptr+GAP
        
        # === Identification ===
        # + (43)
        D(43)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(1); L(2); C()
        I(43)
        
        # , (44)
        D(44)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(2); L(2); C()
        I(44)
        
        # - (45)
        D(45)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(3); L(2); C()
        I(45)
        
        # . (46)
        D(46)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(4); L(2); C()
        I(46)
        
        # < (60)
        D(60)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(5); L(2); C()
        I(60)
        
        # > (62)
        D(62)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(6); L(2); C()
        I(62)
        
        # Cleanup Char, Flag. Move to ID (Ptr+GAP+1)
        Z(); R(1); Z(); R(1)
        
        # === Emission ===
        # We are at ID (Ptr+GAP+1). Flag is at Ptr+GAP+2.
        # To go to Ptr, we need L(GAP+1).
        
        # ID=1 (+) -> fe 03 (2 bytes)
        D(1)
        R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1); B(); D()
        # Move Ptr+1(Cnt) to Ptr+3. Inc.
        L(GAP+2); R(1); Z(); I(1); L(1); B(); R(2); I(1); L(2); D(); C(); R(2); I(2); L(3)
        # Write 2 bytes
        Z(); I(0xfe); R(1)
        Z(); I(0x03); R(1)
        # Return to Flag: Gap+2 - 2 = Gap
        R(GAP)
        C()
        
        # ID=2 (,) -> syscall read (23 bytes)
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1); B(); D()
        # Move Cnt to Ptr+24. Add 23.
        L(GAP+2); R(1); Z(); I(1); L(1); B(); R(23); I(1); L(23); D(); C(); R(23); I(23); L(24)
        # Write 23 bytes
        emit_bytes([0x48, 0xc7, 0xc0, 0x00, 0x00, 0x00, 0x00])
        emit_bytes([0x48, 0xc7, 0xc7, 0x00, 0x00, 0x00, 0x00])
        emit_bytes([0x48, 0x89, 0xde])
        emit_bytes([0x48, 0xc7, 0xc2, 0x01, 0x00, 0x00, 0x00])
        emit_bytes([0x0f, 0x05])
        # Return: Gap+2 - 23 = Gap-21
        R(GAP-21)
        C()
        
        # ID=3 (-) -> fe 0b (2 bytes)
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1); B(); D()
        L(GAP+2); R(1); Z(); I(1); L(1); B(); R(2); I(1); L(2); D(); C(); R(2); I(2); L(3)
        emit_bytes([0xfe, 0x0b])
        R(GAP)
        C()
        
        # ID=4 (.) -> syscall write (23 bytes)
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1); B(); D()
        L(GAP+2); R(1); Z(); I(1); L(1); B(); R(23); I(1); L(23); D(); C(); R(23); I(23); L(24)
        emit_bytes([0x48, 0xc7, 0xc0, 0x01, 0x00, 0x00, 0x00])
        emit_bytes([0x48, 0xc7, 0xc7, 0x01, 0x00, 0x00, 0x00])
        emit_bytes([0x48, 0x89, 0xde])
        emit_bytes([0x48, 0xc7, 0xc2, 0x01, 0x00, 0x00, 0x00])
        emit_bytes([0x0f, 0x05])
        R(GAP-21)
        C()
        
        # ID=5 (<) -> 48 ff cb (3 bytes)
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1); B(); D()
        L(GAP+2); R(1); Z(); I(1); L(1); B(); R(3); I(1); L(3); D(); C(); R(3); I(3); L(4)
        emit_bytes([0x48, 0xff, 0xcb])
        # Return: Gap+2 - 3 = Gap-1
        R(GAP-1)
        C()
        
        # ID=6 (>) -> 48 ff c3 (3 bytes)
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1); B(); D()
        L(GAP+2); R(1); Z(); I(1); L(1); B(); R(3); I(1); L(3); D(); C(); R(3); I(3); L(4)
        emit_bytes([0x48, 0xff, 0xc3])
        R(GAP-1)
        C()
        
        # Cleanup
        Z(); L(1); Z()
        L(GAP+1) # Back to Ptr
        
        # Read Next to Ptr+2
        R(2); N()
        I(1); B(); D(1); C()
        L(2)
    C()
    
    # Exit Syscall (12 bytes)
    R(1); Z(); I(1); L(1); B(); R(12); I(1); L(12); D(); C(); R(12); I(12); L(13)
    emit_bytes([0x48, 0xc7, 0xc0, 0x3c, 0x00, 0x00, 0x00])
    emit_bytes([0x48, 0x31, 0xff])
    emit_bytes([0x0f, 0x05])
    
    # === Rewind and Dump ===
    # Ptr is at End. Ptr+1 is Counter.
    # Move Counter to Ptr.
    R(1); B(); L(1); I(1); R(1); D(); C(); L(1)
    # Loop Counter
    B()
        # Move Ptr(Counter) to Ptr-1
        L(1); Z(); I(1); L(1); B(); R(2); I(1); L(2); D(); C()
        R(2); B(); L(2); I(1); R(2); D(); C(); L(1)
        D(1)
    C()
    
    # Dump 500 bytes
    R(1)
    I(250); B(); O(); R(1); O(); R(1); D(); C()

if __name__ == "__main__":
    main()
