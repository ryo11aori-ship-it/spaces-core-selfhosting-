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
    # Safe Debug: Uses R(10) to avoid clashing with Next Instruction (at R1)
    R(10)
    Z()
    I(char_code)
    O()
    Z()
    L(10)

def main():
    # Headroom
    R(1000)
    DEBUG(83) # S
    
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
    DEBUG(82) # R
    R(100)
    
    # 3. Reset
    L(1)
    B()
    L(1)
    C()
    R(1)
    
    # 4. Exec Loop
    L(100)
    DEBUG(76) # L
    R(100)
    
    B() # Main Loop
    
    # === Safe Check Block Template ===
    # We need to check if Current == TARGET without destroying Current or Next.
    # Layout: [Acc(L1), Current, Next(R1), Gap(R2), Gap(R3)...]
    # Strategy:
    # 1. Sub TARGET from Current.
    # 2. Move Next(R1) to Temp(R2).
    # 3. Set Flag(R1) = 1.
    # 4. Move Current to Temp(R3).
    # 5. Check Temp(R3): If NonZero -> Set Flag(R1)=0. Move Temp(R3) back to Current.
    # 6. Restore Next(R2->R1).
    # 7. Now Flag(R1) is 1 if Match, 0 if NoMatch.
    # 8. If Flag(R1): Do Action.
    # 9. Add TARGET back to Current.
    
    # --- Check + (43) ---
    D(43)
    # Move Next(R1) to R2
    R(1); B(); R(1); I(1); L(1); D(); C(); L(1)
    # Set Flag(R1) = 1
    R(1); I(1); L(1)
    # Move Current to R3
    B(); R(3); I(1); L(3); D(); C()
    # Check R3
    R(3)
    B()
      # R3 is non-zero (No Match)
      L(2); D(); R(2) # Flag(R1) = 0
      L(3); I(1); R(3) # Restore Current (partial)
      D() # Dec R3
    C()
    L(3)
    # Restore Next (R2 -> R1)
    R(2); B(); L(1); I(1); R(1); D(); C(); L(2)
    # Check Flag(R1)
    R(1)
    B()
       # Match!
       D() # Zero Flag
       L(1) # Go to Current
       # Action +
       # DEBUG(43)
       L(1); I(1); R(1)
       R(1) # Go back to Flag
    C()
    L(1)
    I(43) # Restore
    
    # --- Check - (45) ---
    D(45)
    # Move Next(R1) to R2
    R(1); B(); R(1); I(1); L(1); D(); C(); L(1)
    # Set Flag(R1) = 1
    R(1); I(1); L(1)
    # Move Current to R3
    B(); R(3); I(1); L(3); D(); C()
    # Check R3
    R(3); B(); L(2); D(); R(2); L(3); I(1); R(3); D(); C(); L(3)
    # Restore Next
    R(2); B(); L(1); I(1); R(1); D(); C(); L(2)
    # Check Flag
    R(1)
    B()
       D(); L(1)
       # Action -
       # DEBUG(45)
       L(1); D(1); R(1)
       R(1)
    C()
    L(1)
    I(45)

    # --- Check . (46) ---
    D(46)
    # Move Next(R1) to R2
    R(1); B(); R(1); I(1); L(1); D(); C(); L(1)
    # Set Flag(R1) = 1
    R(1); I(1); L(1)
    # Move Current to R3
    B(); R(3); I(1); L(3); D(); C()
    # Check R3
    R(3); B(); L(2); D(); R(2); L(3); I(1); R(3); D(); C(); L(3)
    # Restore Next
    R(2); B(); L(1); I(1); R(1); D(); C(); L(2)
    # Check Flag
    R(1)
    B()
       D(); L(1)
       # Action .
       L(1); O(); R(1)
       R(1)
    C()
    L(1)
    I(46)

    # --- Check , (44) ---
    D(44)
    # Move Next(R1) to R2
    R(1); B(); R(1); I(1); L(1); D(); C(); L(1)
    # Set Flag(R1) = 1
    R(1); I(1); L(1)
    # Move Current to R3
    B(); R(3); I(1); L(3); D(); C()
    # Check R3
    R(3); B(); L(2); D(); R(2); L(3); I(1); R(3); D(); C(); L(3)
    # Restore Next
    R(2); B(); L(1); I(1); R(1); D(); C(); L(2)
    # Check Flag
    R(1)
    B()
       D(); L(1)
       # Action ,
       # DEBUG(44)
       L(1); N(); R(1)
       R(1)
    C()
    L(1)
    I(44)

    # --- Advance ---
    L(1)
    B(); D(); R(2); I(1); L(2); C()
    R(1)
    B(); D(); L(1); I(1); R(1); C()
    R(1)
    B(); D(); L(1); I(1); R(1); C()
    L(1)
    R(1)
    
    C() # End Loop
    
    L(100)
    DEBUG(69) # E
    R(100)

if __name__ == "__main__":
    main()
