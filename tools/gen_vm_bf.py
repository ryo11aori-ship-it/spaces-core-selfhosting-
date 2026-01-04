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
    # SAFETY: Headroom
    R(1000)
    
    DEBUG(83) # 'S'
    
    # 1. Setup Sentinel
    Z()
    I(255)

    # 2. Read Code
    R(100)
    N()
    B()
    R(1)
    N()
    C()
    
    L(100)
    DEBUG(82) # 'R'
    R(100)
    
    # 3. Reset
    L(1)
    B()
    L(1)
    C()
    R(1)
    
    # 4. Exec Loop
    L(100)
    DEBUG(76) # 'L'
    R(100)
    
    B() # Main Loop Start
    
    # --- Check + (43) ---
    D(43)
    R(1); Z(); I(1); L(1) # Temp=1
    B(); R(1); D(); L(1); B(); L(1); C(); C() # Zero Temp if Current!=0
    R(1)
    B() # If Temp!=0 (Match)
    D() # Zero Temp
    L(1) # Go to Current
    # Action +
    L(1); I(1); R(1) # Inc Acc
    R(1) # <--- FIX: Move back to Temp to match "No Match" state
    C()
    L(1) # Back to Current
    I(43) # Restore
    
    # --- Check - (45) ---
    D(45)
    R(1); Z(); I(1); L(1)
    B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1)
    B()
    D()
    L(1)
    # Action -
    L(1); D(1); R(1)
    R(1) # FIX
    C()
    L(1)
    I(45)
    
    # --- Check . (46) ---
    D(46)
    R(1); Z(); I(1); L(1)
    B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1)
    B()
    D()
    L(1)
    # Action .
    L(1); O(); R(1)
    R(1) # FIX
    C()
    L(1)
    I(46)
    
    # --- Check , (44) ---
    D(44)
    R(1); Z(); I(1); L(1)
    B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1)
    B()
    D()
    L(1)
    # Action ,
    L(1); N(); R(1)
    R(1) # FIX
    C()
    L(1)
    I(44)
    
    # --- Advance ---
    # Move [Acc, Instr, Next] -> [Instr, Acc, Next] -> [Instr, Acc, Next(Head)]
    L(1)
    B(); D(); R(2); I(1); L(2); C()
    R(1)
    B(); D(); L(1); I(1); R(1); C()
    R(1)
    B(); D(); L(1); I(1); R(1); C()
    L(1)
    R(1)
    
    C() # Main Loop End
    
    L(100)
    DEBUG(69) # 'E'
    R(100)

if __name__ == "__main__":
    main()
