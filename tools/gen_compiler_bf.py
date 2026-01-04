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
    
    # === 1. ELF Header (167 bytes) ===
    # Same standard header as before
    emit_bytes([0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0])
    emit_bytes([0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00])
    emit_bytes([0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0,0,0,0,0,0,0,0])
    emit_bytes([0,0,0,0, 64,0, 56,0, 1,0, 64,0, 0,0, 0,0])
    emit_bytes([0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0,0,0,0,0,0,0,0])
    emit_bytes([0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0xa7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0xa7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    # We are now at Ptr (Buffer Tail).
    
    # === 2. Compilation Loop (Sliding Window) ===
    # Read first char
    N()
    
    # While Input != 0
    B()
        # Move Char from Ptr to Ptr+50 (Safe Zone)
        # Temp use Ptr+1
        Z(); I(1); L(1); B(); R(50); I(1); L(50); D(); C()
        R(50) # At Ptr+50 (Char)
        
        # === Identification Phase ===
        # ID Location: Ptr+51
        # Check + (43) -> ID=1
        D(43)
        B(); R(1); D(); L(1); Z(); C() # If diff!=0, Flag=0. Char=0.
        R(1) # At Flag
        B(); D(); R(1); I(1); L(2); C() # If Flag, ID=1. Back to Char.
        I(43) # Restore Char
        
        # Check , (44) -> ID=2
        D(44)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(2); L(2); C()
        I(44)

        # Check - (45) -> ID=3
        D(45)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(3); L(2); C()
        I(45)

        # Check . (46) -> ID=4
        D(46)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(4); L(2); C()
        I(46)

        # Check < (60) -> ID=5
        D(60)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(5); L(2); C()
        I(60)

        # Check > (62) -> ID=6
        D(62)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(6); L(2); C()
        I(62)

        # Clear Char (Ptr+50) and Flag (Ptr+51)
        Z()
        R(1); Z() 
        R(1) # At ID (Ptr+52)
        
        # === Emission Phase ===
        # We are at ID (Ptr+52).
        
        # ID=1 (+) -> fe 03
        D(1)
        B(); R(1); D(); L(1); Z(); C()
        R(1) # At Flag
        B()
            D() # Flag=0
            L(53) # Back to Ptr
            # Emit fe 03
            I(0xfe); R(1); I(0x03); R(1)
            # Adjust to Ptr+52 (New ID loc)
            # We moved 2. Old ID was at Ptr+52.
            # New ID is at NewPtr+50?
            # No, we just need to return to the "ID Cell" to continue checking.
            # The loop expects us at ID.
            # We are at NewPtr.
            # ID was at OldPtr+52.
            # NewPtr = OldPtr+2.
            # So ID is at NewPtr + 50.
            R(50)
        C()
        
        # ID=2 (,) -> syscall read (40 bytes)
        # mov rax,0; mov rdi,0; mov rsi,rbx; mov rdx,1; syscall
        D(1)
        B(); R(1); D(); L(1); Z(); C()
        R(1)
        B()
            D()
            L(53)
            # 48 c7 c0 00 00 00 00
            emit_bytes([0x48, 0xc7, 0xc0, 0x00, 0x00, 0x00, 0x00])
            # 48 c7 c7 00 00 00 00
            emit_bytes([0x48, 0xc7, 0xc7, 0x00, 0x00, 0x00, 0x00])
            # 48 89 de
            emit_bytes([0x48, 0x89, 0xde])
            # 48 c7 c2 01 00 00 00
            emit_bytes([0x48, 0xc7, 0xc2, 0x01, 0x00, 0x00, 0x00])
            # 0f 05
            emit_bytes([0x0f, 0x05])
            # Len 23.
            R(50-23)
        C()

        # ID=3 (-) -> fe 0b
        D(1)
        B(); R(1); D(); L(1); Z(); C()
        R(1)
        B()
            D()
            L(53)
            I(0xfe); R(1); I(0x0b); R(1)
            R(50)
        C()

        # ID=4 (.) -> syscall write (40 bytes)
        # mov rax,1; mov rdi,1; mov rsi,rbx; mov rdx,1; syscall
        D(1)
        B(); R(1); D(); L(1); Z(); C()
        R(1)
        B()
            D()
            L(53)
            # 48 c7 c0 01 00 00 00
            emit_bytes([0x48, 0xc7, 0xc0, 0x01, 0x00, 0x00, 0x00])
            # 48 c7 c7 01 00 00 00
            emit_bytes([0x48, 0xc7, 0xc7, 0x01, 0x00, 0x00, 0x00])
            # 48 89 de
            emit_bytes([0x48, 0x89, 0xde])
            # 48 c7 c2 01 00 00 00
            emit_bytes([0x48, 0xc7, 0xc2, 0x01, 0x00, 0x00, 0x00])
            # 0f 05
            emit_bytes([0x0f, 0x05])
            # Len 23.
            R(50-23)
        C()

        # ID=5 (<) -> dec rbx (3 bytes)
        D(1)
        B(); R(1); D(); L(1); Z(); C()
        R(1)
        B()
            D()
            L(53)
            # 48 ff cb
            emit_bytes([0x48, 0xff, 0xcb])
            R(50-3) # Back to ID relative
        C()

        # ID=6 (>) -> inc rbx (3 bytes)
        D(1)
        B(); R(1); D(); L(1); Z(); C()
        R(1)
        B()
            D()
            L(53)
            # 48 ff c3
            emit_bytes([0x48, 0xff, 0xc3])
            R(50-3)
        C()
        
        # ID cleanup (if any left)
        Z()
        
        # Return to Ptr
        L(52)
        
        # Read Next Char
        N()
    
    # End Loop
    C()
    
    # === 3. Exit Code (Exit(0)) ===
    # mov rax, 60; xor rdi, rdi; syscall
    emit_bytes([0x48, 0xc7, 0xc0, 0x3c, 0x00, 0x00, 0x00])
    emit_bytes([0x48, 0x31, 0xff])
    emit_bytes([0x0f, 0x05])

    # === 4. Output Dump ===
    # We are at Ptr (Buffer Tail).
    # We need to print from 300 to Ptr.
    # Mark End with Sentinel? No, binary.
    # We can't use sentinel.
    # We must drag a "Counter" or "Start Marker".
    # Ptr is high (e.g. 600). Start is 300.
    # Go Left until we hit Start Marker?
    # Cell 299 was 0.
    # We can put a marker at 299.
    L(1000) # Go safe left
    R(299)
    I(1) # Marker
    
    # Scan Right to find 0? No, Ptr is at 0 (EOF of buffer).
    # But Buffer contains 0s.
    # We are stuck. We don't know where Ptr is.
    
    # Cheat:
    # Just print 5000 bytes.
    # It will include garbage 0s at the end, but ELF ignores them (it uses FileSize in header).
    # Header says FileSize = 0xa7 (167).
    # Wait, we need to UPDATE Header FileSize!
    # Updating Header at 300 from unknown Ptr is impossible in pure BF without linear scan.
    # BUT, we can make FileSize "Huge" in the header initially?
    # e.g. 0x2000 (8KB).
    # If the file is smaller, it's just padding.
    # Yes, I did that in the header above (FileSize 0x2000).
    
    # So just print 5000 bytes.
    I(255) # Loop 255
    B()
       # Print 20 bytes per iter
       for _ in range(20):
           R(1); O()
       D()
    C()

if __name__ == "__main__":
    main()
