#!/usr/bin/env python3
import sys

# Output Helpers
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

def DEBUG(char_code):
    # Use Gap1(R1) as safe temp for debug printing
    R(1); Z(); I(char_code); O(); Z(); L(1)

def main():
    # Setup Headroom & Sentinel
    R(1000)
    Z(); I(255)
    
    # Move to Start of Code (1100)
    R(100)
    
    # Read Loop (Stride 4)
    # Layout: [Code, Gap1, Gap2, Data]
    N()
    B()
    R(4)
    N()
    C()
    
    # Debug: Read Done
    DEBUG(82) # 'R'
    
    # Reset Logic (Stride 4 Left Scan)
    L(4)
    B()
    L(4)
    C()
    R(4) # Land on Start Code
    
    # Debug: Loop Start
    DEBUG(76) # 'L'
    
    # Execution Loop
    B()
    
    # === Check + (43) ===
    D(43)
    # Copy Code(Current) to Gap1(R1) using Gap2(R2) as temp
    # Code [ R1+ R2+ Code- ] R2 [ Code+ R2- ]
    B(); R(1); I(1); R(1); I(1); L(2); D(); C()
    R(2); B(); L(2); I(1); R(2); D(); C(); L(2)
    
    # Now R(1) has copy of (Code-43).
    # Check if R(1) is 0.
    # Set Flag=1 in R(2).
    R(2); Z(); I(1)
    L(1) # At R1
    B()
      R(1) # At R2 (Flag)
      Z() # Flag=0
      L(1) # At R1
      Z() # Clear R1 to exit loop
    C()
    
    # Check Flag at R(2)
    R(2)
    B()
      D() # Zero Flag
      L(2) # Back to Code
      # Action +
      DEBUG(43)
      R(3) # To Data
      I(1)
      L(3) # Back to Code
      I(43) # Restore Code for next loop (optional but clean)
      R(2) # Back to Flag (to exit loop)
    C()
    L(2) # Back to Code

    # === Check , (44) ===
    # Rel check: Code was -43. Dec 1 -> -44.
    D(1)
    # Copy Code to Gap1
    B(); R(1); I(1); R(1); I(1); L(2); D(); C()
    R(2); B(); L(2); I(1); R(2); D(); C(); L(2)
    # Zero Check R(1)
    R(2); Z(); I(1)
    L(1)
    B(); R(1); Z(); L(1); Z(); C()
    # Check Flag R(2)
    R(2)
    B()
      D()
      L(2)
      DEBUG(44)
      R(3); N(); L(3)
      I(44)
      R(2)
    C()
    L(2)

    # === Check - (45) ===
    D(1)
    # Copy
    B(); R(1); I(1); R(1); I(1); L(2); D(); C()
    R(2); B(); L(2); I(1); R(2); D(); C(); L(2)
    # Zero Check
    R(2); Z(); I(1)
    L(1)
    B(); R(1); Z(); L(1); Z(); C()
    # Flag
    R(2)
    B()
      D()
      L(2)
      DEBUG(45)
      R(3); D(1); L(3)
      I(45)
      R(2)
    C()
    L(2)

    # === Check . (46) ===
    D(1)
    # Copy
    B(); R(1); I(1); R(1); I(1); L(2); D(); C()
    R(2); B(); L(2); I(1); R(2); D(); C(); L(2)
    # Zero Check
    R(2); Z(); I(1)
    L(1)
    B(); R(1); Z(); L(1); Z(); C()
    # Flag
    R(2)
    B()
      D()
      L(2)
      # DEBUG(46)
      R(3); O(); L(3)
      I(46)
      R(2)
    C()
    L(2)

    # Restore Code (+46)
    I(46)
    
    # === Advance ===
    # Move Data(R3) to NextData(R3 + 4 = R7)
    # Use R(1) as temp.
    R(3)
    B(); L(2); I(1); R(2); I(1); R(1); D(); C() # Move Data -> Gap1(R1) + Temp(R1+offset? No)
    # Wait, R(3) is Data. R(1) relative to Data is Gap1 of *Next*?
    # No.
    # Current: Code.
    # R3: Data.
    # We want to move Data(R3) to Next Data(R7).
    # Use Gap1(R1) as temp? No, R1 is 0 now.
    # Move R3 -> R7 directly?
    # R3 [ R4+ R3- ]
    # R4 is Gap of next block?
    # Next Block: Code(R4), Gap1(R5), Gap2(R6), Data(R7).
    # Move R3 to R7.
    # R3 [ R4+ R3- ] (Move to R7)
    B(); R(4); I(1); L(4); D(); C()
    
    # Move Head to Next Code (R4)
    L(3) # Back to Code
    R(4)
    
    C()
    DEBUG(69)

if __name__ == "__main__":
    main()
