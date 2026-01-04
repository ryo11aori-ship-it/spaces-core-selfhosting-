#!/usr/bin/env python3
import sys

S = " "
F = "\u3000"

def e(s):
    sys.stdout.write(s + "\n")

def R(n=1):
    if n > 0: e((S + S + S) * n)

def L(n=1):
    if n > 0: e((S + S + F) * n)

def I(n=1):
    if n > 0: e((S + F + S) * n)

def D(n=1):
    if n > 0: e((S + F + F) * n)

def O():
    e(F + S + S)

def N():
    e(F + S + F)

def B():
    e(F + F + S)

def C():
    e(F + F + F)

def Z():
    B()
    D()
    C()

def DEBUG(char_code):
    R(1)
    Z()
    I(char_code)
    O()
    Z()
    L(1)

def main():
    # SAFETY: Move right 1000 cells to prevent underflow during left scans.
    R(1000)
    
    # Diagnostic: Start 'S'
    DEBUG(83)
    
    # Memory Layout (Relative to 1000):
    # 0: Sentinel (255)
    # 1-99: Registers / Gap
    # 100+: Code Segment
    
    # 1. Setup Sentinel (255) at 0
    Z()
    I(255)

    # 2. Read Code into 100+
    R(100)
    N()
    B()
    R(1)
    N()
    C()
    
    # Diagnostic: Read Done 'R'
    # We are at EOF (0).
    # We need to go back to 100.
    # Safe Scan Left: Scan until we hit a 0 value in the GAP (1-99).
    # Since 1-99 are 0, and Code is non-zero, this works.
    # BUT, we might overshoot if Code contains 0?
    # BF Code shouldn't contain 0.
    
    # To be safer: We scan left until we hit 255 (Sentinel at 0).
    L(1)
    B()
    # Check if 255
    # Copy current to Temp(R1)
    # Subtract 255. If 0, we found it.
    # If not 0, Restore and Move Left.
    
    # Simplified Scan: Just scan left until non-zero? No, code is non-zero.
    # Scan left until 255?
    # Or just scan left until we hit the Gap (0)?
    # Assuming code doesn't have 0.
    
    # Let's try the Gap Scan again, but with Headroom, it won't crash even if it goes too far.
    L(1)
    C()
    
    DEBUG(82) # 'R'
    
    # Now we are at the Gap (somewhere 1-99).
    # We need to go Right to 100.
    # Scan Right until Non-Zero?
    R(1)
    B()
    # If 0, R(1).
    # Wait, how to scan for non-zero in a sea of zeros?
    # [>]+ logic? No.
    # We know 100 is start.
    # We are at 99 (likely).
    # Just move R(1).
    # If we overshoot left scan into 0..99, we are at largest 0 index.
    # Actually, the loop `L(1); B(); L(1); C()` stops at the FIRST 0 it finds from the right.
    # So it stops at 99.
    # So we are at 99.
    # Move R(1) -> 100.
    # This is correct.
    
    # 3. Execution Loop
    # Diagnostic: Loop Start 'L'
    DEBUG(76)
    
    B()
    
    # Check + (43)
    D(43)
    R(1)
    Z()
    I(1)
    L(1)
    B()
    R(1)
    D()
    L(1)
    B()
    L(1)
    C()
    C()
    R(1)
    B()
    D()
    L(1)
    
    # Action +
    # We need to access Data Tape.
    # Data Tape is far away? No, we use Bubble Strategy.
    # Left(1) is Accumulator.
    # Left(1) relative to 1000+ is safe.
    L(1)
    I(1)
    R(1)
    
    C()
    L(1)
    I(43) # Restore
    
    # Check . (46)
    D(46)
    R(1)
    Z()
    I(1)
    L(1)
    B()
    R(1)
    D()
    L(1)
    B()
    L(1)
    C()
    C()
    R(1)
    B()
    D()
    L(1)
    
    # Action . (Output)
    L(1)
    O()
    R(1)
    
    C()
    L(1)
    I(46) # Restore
    
    # Advance (Bubble Move)
    L(1)
    B()
    D()
    R(2)
    I(1)
    L(2)
    C()
    R(1)
    B()
    D()
    L(1)
    I(1)
    R(1)
    C()
    R(1)
    B()
    D()
    L(1)
    I(1)
    R(1)
    C()
    L(1)
    R(1)
    
    C() # End of Main Loop
    
    # Diagnostic: End 'E'
    DEBUG(69)

if __name__ == "__main__":
    main()
