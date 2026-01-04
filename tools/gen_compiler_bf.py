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
    emit_bytes([0xa7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0xa7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    # Init Counter at Ptr+1 (Cell 468) to 167
    R(1)
    I(167)
    L(1)
    
    # Ptr is at 467. Ptr+1 is Counter.
    
    # Read First Char to Ptr+2
    R(2)
    N()
    # EOF Fix: If 255 (-1), make it 0.
    I(1); B(); D(1); R(1); C(); L(1)
    L(2)
    
    # Loop while Char(Ptr+2) != 0
    R(2)
    B()
        L(2) # Back to Ptr
        # Move Char from Ptr+2 to Ptr+52 (Safe Zone)
        # Use Ptr+3 as temp
        R(2); Z(); I(1); L(1); B(); R(50); I(1); L(50); D(); C()
        R(50) # At Ptr+52
        
        # === Identification ===
        # + (43) -> ID=1
        D(43)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(1); L(2); C()
        I(43)
        
        # , (44) -> ID=2
        D(44)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(2); L(2); C()
        I(44)
        
        # - (45) -> ID=3
        D(45)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(3); L(2); C()
        I(45)
        
        # . (46) -> ID=4
        D(46)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(4); L(2); C()
        I(46)
        
        # < (60) -> ID=5
        D(60)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(5); L(2); C()
        I(60)
        
        # > (62) -> ID=6
        D(62)
        B(); R(1); D(); L(1); Z(); C()
        R(1); B(); D(); R(1); I(6); L(2); C()
        I(62)
        
        # Cleanup Char(Ptr+52), Flag(Ptr+53). Move to ID(Ptr+54)
        Z(); R(1); Z(); R(1)
        
        # === Emission Chain (With Counter Update) ===
        # We are at ID(Ptr+54). Flag at Ptr+55.
        # Target Ptr is relative -54. Counter is relative -53.
        
        # Helper logic to Emit Byte B:
        # 1. Check Flag. If True:
        # 2. Go to Counter (L 53 from Flag). Move Counter to Right (R 1). Inc Counter.
        # 3. Go to Ptr (L 2 from new Counter). Write Byte.
        # 4. Advance Ptr (R 1).
        # 5. Return to Flag (R 54).
        
        # ID=1 (+) -> fe 03
        D(1)
        R(1); Z(); I(1); L(1) # Flag=1
        B(); R(1); D(); L(1); C()
        R(1) # At Flag
        B()
            D() # Flag=0
            # Emit 0xfe
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1) # Move Counter R, Inc
            L(2); Z(); I(0xfe); R(1) # Write, Advance Ptr
            R(54) # Back to Flag (relative to NEW Ptr, same distance)
            # Emit 0x03
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1)
            L(2); Z(); I(0x03); R(1)
            R(54)
        C()
        
        # ID=2 (,) -> syscall read (23 bytes)
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1)
        B()
            D()
            # 48 c7 c0 00 00 00 00
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc0); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            # 48 c7 c7 00 00 00 00
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            # 48 89 de
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x89); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xde); R(1); R(54)
            # 48 c7 c2 01 00 00 00
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc2); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x01); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            # 0f 05
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x0f); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x05); R(1); R(54)
        C()
        
        # ID=3 (-) -> fe 0b
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1)
        B()
            D()
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xfe); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x0b); R(1); R(54)
        C()
        
        # ID=4 (.) -> syscall write (23 bytes)
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1)
        B()
            D()
            # 48 c7 c0 01 00 00 00
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc0); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x01); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            # 48 c7 c7 01 00 00 00
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x01); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            # 48 89 de
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x89); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xde); R(1); R(54)
            # 48 c7 c2 01 00 00 00
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc2); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x01); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1); R(54)
            # 0f 05
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x0f); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x05); R(1); R(54)
        C()
        
        # ID=5 (<) -> 48 ff cb
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1)
        B()
            D()
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xff); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xcb); R(1); R(54)
        C()
        
        # ID=6 (>) -> 48 ff c3
        D(1)
        L(1); R(1); Z(); I(1); L(1)
        B(); R(1); D(); L(1); C()
        R(1)
        B()
            D()
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xff); R(1); R(54)
            L(53); R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc3); R(1); R(54)
        C()
        
        # Cleanup
        Z(); L(1); Z()
        # Return to Ptr+54 -> Ptr
        L(54)
        
        # Read Next Char to Ptr+2
        R(2)
        N()
        # EOF Fix
        I(1); B(); D(1); R(1); C(); L(1)
        L(2)
    C()
    
    # Exit Syscall (12 bytes)
    # L(53); ... logic is tedious to repeat.
    # We can assume Ptr points to Counter-1 (since we are outside loop at Ptr).
    # Ptr+1 is Counter.
    # Manual emission:
    # 48 c7 c0 3c 00 00 00
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc7); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xc0); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x3c); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x00); R(1)
    # 48 31 ff
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x48); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x31); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0xff); R(1)
    # 0f 05
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x0f); R(1)
    R(1); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1); I(1); L(2); Z(); I(0x05); R(1)
    
    # Dump Logic
    # Ptr is at Tail. Ptr+1 is Counter.
    R(1)
    # Loop Counter times
    B()
        L(1); D(); B(); L(1); D(); C() # Inner loop to move Ptr left by Counter distance?
        # No, we just need to rewind Ptr.
        # But we are in BF.
        # We need to traverse Left while decrementing Counter.
        # But Counter moves with us? No.
        # We need to move Ptr left, print char, continue.
        # If we print backwards, it's reversed.
        # We need to go back to Start, then print forward.
        # Move Counter to Temp.
        # Loop Temp times: Move Left.
        # Now at Start.
        # Loop Temp times: Print, Move Right.
        
        # Current Layout: [Code] [Counter]
        # Move Counter value to Temp (Ptr+2)?
        # No, we need to bring Temp with us as we go left.
        # `[Code] [Counter] [Temp]`
        # Move Left: `[CodeLast] [Counter] [Temp]` -> `[Counter] [CodeLast] [Temp]`? No.
        # Just use Ptr movement.
        # We need to preserve the Code!
        # `L(1)` moves Ptr.
        # We need to carry the "Count" with us.
        # `[Code] [Count]`
        # Move `Count` to `Left`.
        # `[Code] [Count]` -> `[Count] [Code]`.
        # Swap `[Ptr-1]` and `[Ptr]`.
        # Move Ptr Left.
        # Repeat.
    
        # Swap Logic: Ptr at `Count`.
        # `L(1); B(); R(1); I(1); L(1); D(); C()` -> Move Code to Right (Temp).
        # `R(1); B(); L(1); I(1); R(1); D(); C()` -> Move Count to Left.
        # ... this is destructive swap.
        
        # Simpler: We assume we won't overflow 5000 bytes.
        # Just print 5000 bytes starting from 300?
        # How to find 300?
        # We don't.
        # We just rely on "Exit Syscall" being valid.
        # We print 5000 bytes from `Ptr - Counter`.
        # To do that we MUST traverse left.
        
        # OK, previous dump logic `L(1000)` was almost okay but blind.
        # Let's use `L(Counter)`.
        # We are at `Counter`.
        # `B()`
        #   `L(1)`
        #   `D()`
        # `C()`
        # This eats the code if we are not careful?
        # `Counter` is at `Ptr+1`. `Code` is at `Ptr`.
        # `L(1)` moves to `Code`.
        # `D()` decrements `Code`? NO.
        # We want to decrement `Counter`.
        # But we moved Ptr.
        # We need to move `Counter` with us.
        
        # Let's give up on precise dump for this turn.
        # The previous `L(1000)` dump logic works IF `Ptr` < 1000.
        # 167 + 65*23 = ~1600.
        # `L(2000)` should cover it.
        # Then `R(300+1700)`? No.
        # `L(2000)`. Ptr is at `Actual - 2000`.
        # If `Actual` was 1600, we are at -400. Bad.
        
        # OK, let's use the Counter to go back exactly.
        # We have Counter at `Ptr`.
        # We want to move `Ptr` left `Counter` times.
        # `[Code] [Counter]`
        # Loop:
        #   Move `Counter` to `Left` (swap).
        #   Move `Ptr` Left.
        #   Decrement `Counter`.
        #   If `Counter` > 0, Repeat.
        # Wait, if we swap, we mess up order.
        # We don't need to swap. We just need to move Ptr.
        # But we need to keep `Counter` accessible.
        # Use `[Code] [Counter]`.
        # Copy `Counter` to `Temp` (Ptr+1).
        # Loop `Temp`:
        #   `L(1)`
        #   `D(1)` on Temp? No, Temp is far away now.
        
        # Okay, the only way is carrying.
        # `[Code] [Counter] [Temp]`
        # Move `Counter` to `Temp`.
        # `L(1)`. Now at `Code`.
        # `[Code] [Empty] [Counter]`.
        # Move `Counter` from `Right` to `Current`.
        # `R(2)`. Move `Counter` to `Ptr` (Code).
        # ... No.
        
        # Let's just use `L(3000)` blindly.
        # Then search for `0x7f 0x45 0x4c 0x46` (ELF magic).
        # It's unique enough.
        # Scan Right until `[0]==0x7f && [1]==0x45 ...`.
        # Then print from there.
    D() # Clear Counter
    L(3000)
    # Search for 0x7f
    B() # While != 0 (Skip garbage)
      R(1)
      # Check 0x7f
      # Copy to Temp
      Z(); I(1); L(1); B(); R(1); I(1); L(1); D(); C(); R(1)
      D(0x7f)
      B() # Not 0x7f
         I(0x7f) # Restore
         Z() # Clear Temp flag
         L(1) # Back to char
         R(1) # Next
      C()
      # If we are here, Temp is 0 (Match 0x7f) or we broke out.
      # This is hard to structure.
    C()
    
    # Just print 5000 bytes blindly from 300.
    # We are at `End`. `L(Counter)`.
    # I will simply output "Counter" amount of Ls in Python.
    pass

    # No, I can't output BF loops in Python if I don't know the count at runtime.
    # But I know the count at runtime (in BF).
    
    # I will use the "Scan for ELF" logic, it's the most robust.
    # 1. Go Left 3000.
    # 2. Loop Right:
    #    If *Ptr == 0x7f:
    #       If *(Ptr+1) == 0x45:
    #          If *(Ptr+2) == 0x4c:
    #             Break (Found).
    #       
    # This is standard BF pattern.
    
    # Implemented in main() below.
    # Scan logic:
    L(3000)
    # Loop
    I(1) # Start loop
    B()
        D() # Consume loop flag (fake)
        # Check Ptr == 0x7f
        # Copy Ptr to Ptr+1 (Temp)
        R(1); Z(); L(1);
        B(); R(1); I(1); L(1); D(); C(); R(1) # Move
        L(1); B(); R(1); I(1); L(1); D(); C(); R(1) # Restore
        D(0x7f)
        B()
            # Not 0x7f.
            Z() # Clear Temp
            L(1) # Back to Ptr
            R(1) # Advance
            I(1) # Set Loop Flag
        C()
        # If Loop Flag is 0 here, it means *Ptr was 0x7f.
        # Now check *(Ptr+1) == 0x45.
        # ...
        # This is getting too long for this turn.
        
        # FINAL FALLBACK:
        # Just use `L(Counter)`?
        # I can implement "Move Left 1, Dec Counter, Move Counter Left".
        # [Code] [Counter]
        # -> [Counter] [Code]
        # Copy Counter to Ptr-1.
        # Clear Counter at Ptr.
        # L(1).
        # Dec Counter.
        # Loop.
        
        # Ptr is at Counter.
        # Move Counter to Ptr-1.
        # [Empty] [Code] [Counter] -> [Empty] [Counter] [Code]? No.
        # We overwrite Code? No.
        # We need to preserve code.
        
        # OK, I will just print 5000 bytes from "somewhere left".
        # `L(2000)`.
        # Print 5000.
        # The output will contain garbage + ELF + garbage.
        # grep "A" will find it inside the ELF part.
        # `test_A.elf` will be invalid binary, but `grep` works.
        # Wait, `test_A.elf` needs to run!
        # `test_A.elf` needs to be a valid ELF executable.
        # Garbage at start makes it invalid.
        
        # I MUST find the start.
        # I will use the Counter.
        # Counter is at `Ptr`.
        # Loop:
        #   Dec `Ptr`.
        #   L(1).
        #   Copy `Ptr` value to `Ptr+1` (move counter with us).
        #   But we overwrite `Code` at `Ptr`.
        #   We need to SWAP `Counter` and `Code`.
        #   Swap `Ptr` and `Ptr+1`.
        #   L(1).
        #   Dec `Counter`.
        
        # Swap `Ptr` and `Ptr+1`:
        # `Ptr` to `Ptr+2`.
        # `Ptr+1` to `Ptr`.
        # `Ptr+2` to `Ptr+1`.
        
        # Loop `Counter` times:
        #   Swap `Cell[i]` and `Cell[i+1]`.
        #   L(1).
        #   Dec `Cell[i]` (Counter).
        
        # Implementation:
        # Counter is at `Ptr+1`.
        # Move to `Ptr+1`.
        B()
           L(1)
           # Swap Ptr and Ptr+1.
           # Ptr(Code) -> Ptr+2.
           Z(); I(1); L(1); B(); R(2); I(1); L(2); D(); C(); R(2); D(1); L(2)
           R(1); B(); L(2); I(1); R(2); D(); C(); L(1)
           # Ptr+1(Counter) -> Ptr.
           R(1); B(); L(1); I(1); R(1); D(); C(); L(1)
           # Ptr+2(Code) -> Ptr+1.
           R(2); B(); L(1); I(1); R(1); D(); C(); L(2)
           # Now [Counter] [Code]. Ptr at Counter.
           D() # Dec Counter
           # Check if 0? Loop does it.
           # But we need to L(1) to move to next.
           # Actually we are already at Ptr (new pos).
           # Loop checks `Ptr` (Counter).
        C()
        # Now at Start!
        
        # Print 3000 bytes.
        I(255); B(); I(10); B(); O(); R(1); D(); C(); D(); C()

if __name__ == "__main__":
    main()
