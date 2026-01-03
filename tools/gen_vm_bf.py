#!/usr/bin/env python3
import sys

# --- Spaces Dialect ---
S=" "; F="\u3000"
def e(s): sys.stdout.write(s+"\n")
def R(n=1): 
    if n>0: e((S+S+S)*n)
def L(n=1): 
    if n>0: e((S+S+F)*n)
def I(n=1): 
    if n>0: e((S+F+S)*n)
def D(n=1): 
    if n>0: e((S+F+F)*n)
def O(): e(F+S+S)
def N(): e(F+S+F)
def B(): e(F+F+S)
def C(): e(F+F+F)
def Z(): B(); D(); C()

def main():
    # Memory Layout:
    # 0-99: Scratch / Registers
    # 100+: Code Segment
    # 1000+: Data Tape for the Guest Program
    
    # 1. Setup Sentinel at 0
    Z(); I(255)

    # 2. Read Code into 100+
    R(100)
    N() # Read first char
    B() # While char != 0
    R(1); N() # Read next
    C()
    
    # 3. Reset to Start of Code (100)
    # We are currently at EOF (0) at the end of code.
    # The space between 0 and 100 is all 0s.
    # The code chars are non-zero.
    # We scan left until we hit a 0 (which is the gap at 99), then go Right 1.
    L(1)
    B(); L(1); C() # Scan Left while != 0. Stops at 99 (or 0 sentinel).
    R(1) # At 100
    
    # 4. Execution Loop
    # While Code[IP] != 0
    B()
    # Check + (43)
    D(43)
    # Check if 0 (Temp at Right 1)
    R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1); B(); D(); L(1)
    # Action: Increment Data at 1000
    R(900); I(1); L(900)
    C(); L(1)
    I(43) # Restore
    
    # Check - (45)
    D(45)
    R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1); B(); D(); L(1)
    # Action: Decrement Data at 1000
    R(900); D(1); L(900)
    C(); L(1)
    I(45) # Restore
    
    # Check . (46)
    D(46)
    R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1); B(); D(); L(1)
    # Action: Output Data at 1000
    R(900); O(); L(900)
    C(); L(1)
    I(46) # Restore
    
    # Check , (44)
    D(44)
    R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1); B(); D(); L(1)
    # Action: Input Data at 1000
    R(900); N(); L(900)
    C(); L(1)
    I(44) # Restore
    
    # Move to Next Instruction
    R(1)
    C()

if __name__ == "__main__":
    main()
