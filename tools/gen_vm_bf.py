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
    L(10)
    Z()
    I(char_code)
    O()
    Z()
    R(10)

def main():
    R(1000)
    DEBUG(83)
    Z()
    I(255)
    R(100)
    N()
    B()
    R(2)
    N()
    C()
    DEBUG(82)
    
    # --- Reset Logic Fix ---
    # We are at EOF (0).
    # Move Left 2 to land on the last Code slot (or Gap).
    L(2)
    # Scan Left 2 steps at a time until we hit 0 (Gap).
    # Since Code slots are non-zero, this safely rewinds.
    B()
    L(2)
    C()
    # We are now at Gap (0).
    # Move Right 2 to land on Start Code.
    R(2)
    
    DEBUG(76)
    
    # --- Main Loop ---
    # Memory: [L3(Scratch), L2(PrevCode), L1(Scratch), Current(Code), R1(Acc), R2(NextCode), R3(NextAcc)]
    B()
    
    # Check + (43)
    D(43)
    # Use L(1) as Flag, L(3) as Temp.
    # Set Flag=1
    L(1)
    Z()
    I(1)
    # Move Current to L(3)
    R(1)
    B()
    L(3)
    I(1)
    R(3)
    D()
    C()
    # Check L(3) (It holds the difference)
    L(3)
    B()
    # Diff != 0 -> Flag=0
    R(2)
    D()
    L(2)
    # Restore L(3) to Current later? No, clear L(3)
    D()
    C()
    # Check Flag(L1)
    R(2)
    B()
    D()
    R(1)
    DEBUG(43)
    R(1)
    I(1)
    L(1)
    L(1)
    C()
    R(1)
    I(43)
    
    # Check - (45)
    D(45)
    L(1)
    Z()
    I(1)
    R(1)
    B()
    L(3)
    I(1)
    R(3)
    D()
    C()
    L(3)
    B()
    R(2)
    D()
    L(2)
    D()
    C()
    R(2)
    B()
    D()
    R(1)
    DEBUG(45)
    R(1)
    D(1)
    L(1)
    L(1)
    C()
    R(1)
    I(45)
    
    # Check . (46)
    D(46)
    L(1)
    Z()
    I(1)
    R(1)
    B()
    L(3)
    I(1)
    R(3)
    D()
    C()
    L(3)
    B()
    R(2)
    D()
    L(2)
    D()
    C()
    R(2)
    B()
    D()
    R(1)
    # DEBUG(46)
    R(1)
    O()
    L(1)
    L(1)
    C()
    R(1)
    I(46)
    
    # Check , (44)
    D(44)
    L(1)
    Z()
    I(1)
    R(1)
    B()
    L(3)
    I(1)
    R(3)
    D()
    C()
    L(3)
    B()
    R(2)
    D()
    L(2)
    D()
    C()
    R(2)
    B()
    D()
    R(1)
    DEBUG(44)
    R(1)
    N()
    L(1)
    L(1)
    C()
    R(1)
    I(44)
    
    # Advance: Move Acc(R1) to NextAcc(R3)
    R(1)
    B()
    R(2)
    I(1)
    L(2)
    D()
    C()
    
    # Move Head to NextCode(R2)
    R(1) # From R1 to R2
    
    C()
    
    DEBUG(69)

if __name__ == "__main__":
    main()
