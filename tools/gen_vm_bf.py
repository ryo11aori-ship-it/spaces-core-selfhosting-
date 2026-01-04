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
    # Safe Debug: Use far left scratch to verify liveness
    L(10)
    Z()
    I(char_code)
    O()
    Z()
    R(10)

def main():
    # Headroom
    R(1000)
    DEBUG(83) # S
    
    # Setup Sentinel
    Z()
    I(255)
    
    # Interleaved Read Loop: [Code, Data, Code, Data...]
    # Start at 1100 (Code Slot)
    R(100)
    
    # Read First Char
    N()
    B()
      # Spread: Move to next Code slot (Current+2)
      # Current is Code. Next is Data(0). NextNext is Code.
      R(2)
      N()
    C()
    
    DEBUG(82) # R
    
    # Reset Logic: Scan Left for Sentinel (255)
    # Skip 0s (Data slots)
    L(1) # Start moving left
    B() # While Current != 0 (finding Sentinel)
      # If we hit a Data slot (0), this loop would exit? 
      # No, B() checks current.
      # We need a robust scan.
      # Simplified: Just move left until we hit 255.
      # But we will hit 0s.
      # Logic: Move L(1). Check if 255.
      # Brainfuck scan: [ - [->+<] >? ] logic is hard.
      # Since we know the layout is [255, gap(0)..., Code, 0, Code, 0...]
      # And Code != 0.
      # We can just scan L(1) repeat until 255.
      # But B() stops on 0.
      # We are at the end (0 or Code?). Last read put 0 in EOF slot.
      # So we are at 0.
      # Step L(1) -> Code.
      # Loop:
      #   L(1) -> Data (0).
      #   L(1) -> Code/Sentinel.
      #   Check Sentinel.
      
      # Let's implement a specific "Move Left 2" scanner.
      # Current is Code (Non-Zero).
      L(2)
    C()
    # Problem: B() stops on 0. But we jump over 0s with L(2).
    # Sentinel (255) is non-zero. Code is non-zero.
    # The Gap (1-99) is 0.
    # If we jump L(2), we might land in the Gap (0).
    # If we land on 0, B() stops.
    # We want to stop at Sentinel (255)? No, we want to stop at Code Start.
    # Code Start is right after the Gap.
    # So if we hit 0, we went too far?
    # Yes. The Gap is 0.
    # So: Scan Left 2. If 0, we are in Gap. Move Right 2 -> Start of Code.
    R(2)
    
    DEBUG(76) # L
    
    # Exec Loop
    # Head at Instr. Data at R(1).
    B()
    
    # --- Check + (43) ---
    D(43)
    # Check if 0 using L(1) scratch
    R(1); L(2); I(1); R(2); L(1) # Flag = 1 at L1
    B(); L(1); D(); R(1); C() # If Instr!=0, Flag=0
    # Restore Instr? No need, we reconstruct or restore.
    # If Match (Flag=1):
    L(1)
    B()
      D() # Zero Flag
      R(1) # At Instr (0)
      # Action +
      DEBUG(43)
      R(1); I(1); L(1) # Inc Data at R1
      I(43) # Restore Instr
      L(1)
    C()
    R(1) # Back to Instr
    # Restore Instr if not match? 
    # Logic above only restores if match.
    # We must restore blindly? Or check flag?
    # Simpler: Add 43 back.
    # If it was match (0), becomes 43.
    # If not match (X-43), becomes X.
    I(43)
    
    # --- Check - (45) ---
    D(45)
    R(1); L(2); I(1); R(2); L(1)
    B(); L(1); D(); R(1); C()
    L(1)
    B()
      D(); R(1)
      DEBUG(45)
      R(1); D(1); L(1)
      I(45); L(1)
    C()
    R(1); I(45)

    # --- Check . (46) ---
    D(46)
    R(1); L(2); I(1); R(2); L(1)
    B(); L(1); D(); R(1); C()
    L(1)
    B()
      D(); R(1)
      # DEBUG(46)
      R(1); O(); L(1)
      I(46); L(1)
    C()
    R(1); I(46)

    # --- Check , (44) ---
    D(44)
    R(1); L(2); I(1); R(2); L(1)
    B(); L(1); D(); R(1); C()
    L(1)
    B()
      D(); R(1)
      DEBUG(44)
      R(1); N(); L(1)
      I(44); L(1)
    C()
    R(1); I(44)
    
    # --- Advance ---
    # Current: [Instr, Data, NextInstr, NextData]
    # Head at Instr.
    # We want to move Data (at R1) to NextData (at R3).
    # Then move Head to NextInstr (R2).
    
    # Move R(1) to R(3) using R(2) as temp (it is NextInstr, non-zero!)
    # Wait, NextInstr is Code. We cannot overwrite it.
    # We need to move Data to NextData.
    # NextData is 0 (initialized).
    # So we simply move R(1) to R(3).
    # Using L(1) as temp (safe scratch).
    
    R(1)
    B(); L(2); I(1); R(2); D(); C() # Move Data to L1
    L(1)
    B(); R(4); I(1); L(4); D(); C() # Move L1 to R3 (NextData)
    R(1) # Back to R1 (now 0)
    L(1) # Back to Instr
    
    # Move Head to NextInstr
    R(2)
    
    C() # End Loop
    
    DEBUG(69) # E

if __name__ == "__main__":
    main()
