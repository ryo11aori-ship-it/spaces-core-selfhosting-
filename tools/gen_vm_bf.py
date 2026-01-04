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
    L(1)
    B()
    L(2)
    C()
    R(2)
    DEBUG(76)
    B()
    
    # Relative Check Chain:
    # Order: + (43), , (44), - (45), . (46)
    # L(1) is Current Instr.
    
    # --- Check + (43) ---
    D(43)
    # Check if L(1) == 0. Use L(3) as Flag, L(2) as Scratch.
    # Set Flag L(3) = 1
    L(3)
    Z()
    I(1)
    R(3)
    # Copy L(1) to L(2)
    L(1)
    B()
    L(1)
    I(1)
    R(1)
    D()
    C()
    L(2)
    B()
    R(1)
    I(1) # Restore L(1)
    L(2) # At L(2)
    I(1) # Restore L(2)?? No, logic is complex flat.
    # Simple Zero Check:
    # L(1) is value.
    # L(2) = 0.
    # L(1) [ L(2)+ L(1)- ] L(2) [ L(1)+ L(2)- ]
    # This restores L(1).
    # Check Logic:
    # Flag = 1.
    # L(1) [ Flag=0. L(2)+ L(1)- ] L(2) [ L(1)+ L(2)- ]
    D() # L(2)--
    C()
    # Now if L(1) was 0, Flag(L3) is 1. If !=0, Flag is 0.
    # L(1) is restored.
    
    # Let's verify Zero Check Pattern:
    # Temp(L2) [-]
    # Flag(L3) [-]+
    # Val(L1) [ L3[-] L2+ L1- ]
    # L2 [ L1+ L2- ]
    L(2)
    Z()
    L(1)
    I(1) # Flag L(3)=1
    R(2)
    L(1)
    B()
    L(2)
    Z() # Flag=0
    R(1)
    I(1)
    L(1)
    D()
    C()
    L(2)
    B()
    L(1)
    I(1)
    R(1)
    D()
    C()
    # Check Flag (L3)
    L(3)
    B()
    D() # Zero Flag
    R(3) # At R(0)=Head
    # Action +
    DEBUG(43)
    R(1)
    I(1)
    L(1)
    L(3)
    C()
    R(3)

    # --- Check , (44) ---
    # Dec 1 (Total 44)
    L(1)
    D(1)
    R(1)
    # Zero Check L(1)
    L(2)
    Z()
    L(1)
    I(1)
    R(2)
    L(1)
    B()
    L(2)
    Z()
    R(1)
    I(1)
    L(1)
    D()
    C()
    L(2)
    B()
    L(1)
    I(1)
    R(1)
    D()
    C()
    # Check Flag
    L(3)
    B()
    D()
    R(3)
    # Action ,
    DEBUG(44)
    R(1)
    N()
    L(1)
    L(3)
    C()
    R(3)

    # --- Check - (45) ---
    # Dec 1 (Total 45)
    L(1)
    D(1)
    R(1)
    # Zero Check
    L(2)
    Z()
    L(1)
    I(1)
    R(2)
    L(1)
    B()
    L(2)
    Z()
    R(1)
    I(1)
    L(1)
    D()
    C()
    L(2)
    B()
    L(1)
    I(1)
    R(1)
    D()
    C()
    # Check Flag
    L(3)
    B()
    D()
    R(3)
    # Action -
    DEBUG(45)
    R(1)
    D(1)
    L(1)
    L(3)
    C()
    R(3)

    # --- Check . (46) ---
    # Dec 1 (Total 46)
    L(1)
    D(1)
    R(1)
    # Zero Check
    L(2)
    Z()
    L(1)
    I(1)
    R(2)
    L(1)
    B()
    L(2)
    Z()
    R(1)
    I(1)
    L(1)
    D()
    C()
    L(2)
    B()
    L(1)
    I(1)
    R(1)
    D()
    C()
    # Check Flag
    L(3)
    B()
    D()
    R(3)
    # Action .
    # DEBUG(46)
    R(1)
    O()
    L(1)
    L(3)
    C()
    R(3)

    # Restore L(1) (+46)
    L(1)
    I(46)
    R(1)

    # Advance
    R(1)
    B()
    R(2)
    I(1)
    L(2)
    D()
    C()
    R(1)
    C()
    DEBUG(69)

if __name__ == "__main__":
    main()
