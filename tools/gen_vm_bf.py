#!/usr/bin/env python3
import sys

# --- Spaces Dialect ---
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

def main():
    # Memory Layout:
    # 99: Accumulator (Data)
    # 100+: Code Segment
    
    # 1. Setup Sentinel (255) at 0 to prevent overshoot
    Z()
    I(255)

    # 2. Read Code into 100+
    R(100)
    N() # Read first char
    B() # While char != 0
    R(1)
    N() # Read next
    C()
    
    # 3. Reset to Start of Code (100)
    # We are at EOF (0) at the end of input.
    # Scan Left until we find the Accumulator (0) at 99.
    # Note: The area 1-99 is 0. 
    # But Code contains non-zero.
    # We scan left skipping non-zeros (Code).
    # When we hit 0, we assume it's the gap (99).
    L(1)
    B()
    L(1)
    C()
    # Now we are at 99 (Accumulator = 0).
    R(1)
    # Now we are at 100 (Start of Code).
    
    # 4. Execution Loop (Bubble Strategy)
    # Invariant: Head is at Instruction. Left(1) is Accumulator.
    
    B() # While Code[IP] != 0
        # --- EXECUTE ---
        
        # Check + (43)
        D(43)
        # Check if 0 (Temp at Right 1)
        R(1); Z(); I(1); L(1) # Temp=1
        B(); R(1); D(); L(1); B(); L(1); C(); C() # If Data!=0, Temp=0
        R(1); B(); D(); L(1)
        # Action: Increment Accumulator (Left 1)
        L(1); I(1); R(1)
        C(); L(1)
        I(43) # Restore
        
        # Check - (45)
        D(45)
        R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
        R(1); B(); D(); L(1)
        # Action: Decrement Accumulator (Left 1)
        L(1); D(1); R(1)
        C(); L(1)
        I(45) # Restore
        
        # Check . (46)
        D(46)
        R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
        R(1); B(); D(); L(1)
        # Action: Output Accumulator (Left 1)
        L(1); O(); R(1)
        C(); L(1)
        I(46) # Restore
        
        # Check , (44)
        D(44)
        R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
        R(1); B(); D(); L(1)
        # Action: Input Accumulator (Left 1)
        L(1); N(); R(1)
        C(); L(1)
        I(44) # Restore

        # --- ADVANCE (SWAP & MOVE) ---
        # Current: [Acc(L1), Instr(Here), Temp(R1)]
        # Goal:    [Instr(L1), Acc(Here), Temp(R1)] -> Then Move R1
        
        # 1. Move Acc (L1) to Temp (R1)
        L(1)
        B(); D(); R(2); I(1); L(2); C()
        R(1)
        
        # 2. Move Instr (Here) to Acc (L1)
        B(); D(); L(1); I(1); R(1); C()
        
        # 3. Move Temp (R1) to Instr (Here)
        R(1)
        B(); D(); L(1); I(1); R(1); C()
        L(1)
        
        # 4. Move Head Right (to Next Instruction)
        R(1)
    C()

if __name__ == "__main__":
    main()
