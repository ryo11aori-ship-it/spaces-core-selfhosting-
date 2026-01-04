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
    # Debug prints using L(10) to avoid messing with L1-L3 or R1-R...
    # We assume L(10) is safe (gap).
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

    # Read Code
    # Pointer at 1000 (Sentinel). 
    # Move to 1100 for Code Start.
    R(100)
    
    # Read Loop
    N() # Read first char to 1100
    B()
      # DEBUG(114) # 'r' - Diagnostic inside read loop
      R(1)
      N()
    C()
    
    DEBUG(82) # R
    
    # Reset Logic: Scan Left until Sentinel(255)
    # Actually, we can just scan left until we hit the Gap (0) or Sentinel.
    # Gap is 1001-1099. Sentinel is 1000.
    # Code is 1100+.
    # Since we need to start at 1100.
    # Scan left until 0.
    L(1)
    B()
    L(1)
    C()
    R(1)
    
    # We are now at 1100.
    # Ensure L(1), L(2), L(3) are clear (they are in the gap/sentinel area, might be 0).
    # L(1)=1099(0). L(2)=1098(0). L(3)=1097(0). Safe.
    
    DEBUG(76) # L
    
    # Exec Loop
    B()
    
    # === Safe Check Logic using L(2), L(3) ===
    # Current is at P. Next is at R(1).
    # L(1) is Acc. L(2) is T1. L(3) is T2.
    # We use L(2) and L(3) as scratch.
    
    # Template: Check if Current == VAL
    # 1. Move Next(R1) to L(2). (Save Next)
    # 2. Set R(1) as Flag = 1.
    # 3. Move Current(P) to L(3).
    # 4. Sub VAL from L(3).
    # 5. Check L(3). If non-zero:
    #      Set Flag(R1) = 0.
    #      Restore L(3) to Current. (Add VAL back?) No, just move it back.
    #      Wait, if we sub VAL, we must Add VAL to restore? 
    #      Or better: Copy Current to L(3), leave Current intact?
    #      Non-destructive check is hard.
    #      Move Current to L(3). Sub VAL.
    #      If L(3) != 0: Flag=0. Add VAL to L(3). Move L(3) back to Current.
    #      If L(3) == 0: Flag=1. Move L(3) back (it's 0). Restore VAL to Current later?
    #      
    #      Simplified:
    #      Move Current to L(3). Sub VAL.
    #      If L(3) != 0 -> Flag=0.
    #      Add VAL to L(3). Move L(3) back to Current.
    #      Restore Next(L2 -> R1).
    
    # --- Check + (43) ---
    D(43) # Current -= 43
    # Move Next(R1) to L(2)
    R(1); B(); L(3); I(1); R(3); D(); C() # R1->L2 (via bubble logic? No direct jump)
    # Direct jump R1 to L2 is 3 steps left.
    L(3); I(1); R(3) # Set L(2)
    # Wait, simple move:
    L(3); Z(); R(3) # Clear L2
    B(); L(3); I(1); R(3); D(); C() # Move R1 to L2
    
    # Set Flag(R1) = 1
    I(1) # R1 is now 1
    
    # Check Current (which is at P, and is Current-43)
    L(1) # At P
    B() # If Current-43 != 0
      R(1); D(); L(1) # Flag(R1) = 0
      # We don't need to restore Current yet, we are in the 'Else'.
    C()
    
    # Restore Next (L2 -> R1)
    L(2) # At L2
    B(); R(3); I(1); L(3); D(); C() # Move L2 back to R1
    
    # Check Flag(R1)
    R(1) # At Flag
    B()
      # Match! (Current was 43)
      D() # Zero Flag
      L(1) # At Current (which is 0 now)
      # Action +
      DEBUG(43)
      L(1); I(1); R(1) # Inc Acc (L1)
      I(43) # Set Current to 43 (Restore)
      R(1) # Back to Flag (0)
    C()
    # Restore Current if it wasn't a match?
    # If it wasn't a match, Current is (Original - 43).
    # We must add 43 back.
    # But we did that only inside the 'Match' block?
    # We need to add 43 back UNCONDITIONALLY.
    L(1); I(43)
    
    # --- Check - (45) ---
    D(45)
    # Save Next(R1) to L(2)
    R(1); B(); L(3); I(1); R(3); D(); C()
    # Set Flag=1
    I(1)
    # Check Current
    L(1)
    B(); R(1); D(); L(1); C()
    # Restore Next
    L(2); B(); R(3); I(1); L(3); D(); C()
    # Act
    R(1)
    B()
      D(); L(1)
      DEBUG(45)
      L(1); D(1); R(1) # Dec Acc
      R(1)
    C()
    L(1); I(45)

    # --- Check . (46) ---
    D(46)
    R(1); B(); L(3); I(1); R(3); D(); C()
    I(1)
    L(1); B(); R(1); D(); L(1); C()
    L(2); B(); R(3); I(1); L(3); D(); C()
    R(1)
    B()
      D(); L(1)
      # DEBUG(46)
      L(1); O(); R(1)
      R(1)
    C()
    L(1); I(46)

    # --- Check , (44) ---
    D(44)
    R(1); B(); L(3); I(1); R(3); D(); C()
    I(1)
    L(1); B(); R(1); D(); L(1); C()
    L(2); B(); R(3); I(1); L(3); D(); C()
    R(1)
    B()
      D(); L(1)
      DEBUG(44)
      L(1); N(); R(1)
      R(1)
    C()
    L(1); I(44)

    # --- Advance with Bubble (L3, L2, L1, Instr) ---
    # Current state: [L3(T2), L2(T1), L1(Acc), P(Instr), R1(Next)]
    # We want:       [Instr, L3, L2, L1, Next] (Pointer at Next)
    # Effectively shifting Instr Left? No, we move Head Right.
    # So Instr is left behind. L3, L2, L1 must move Right.
    
    # Step 1: Swap L1(Acc) <-> P(Instr)
    L(1)
    B(); R(1); I(1); L(1); D(); C() # Move Acc to P (destructive? No, swap)
    # Actually simpler: Move Acc to Temp(R1? No R1 is Next).
    # Use L(2) as temp? L(2) has data.
    # We need a swap algorithm.
    # Use R(1) as temp? R(1) is Next. Can't overwrite.
    # Use L(3) as temp? Has data.
    
    # Just move ALL of them right?
    # [T2, T1, Acc, Instr, Next]
    # Move Instr to Temp (L4? No).
    # Move Instr to R(1)? No.
    
    # Trick: We only need `Acc` to persist. `Temp1` and `Temp2` are scratch (0).
    # Ah! L(2) and L(3) are SCRATCH. They are expected to be 0 between instructions!
    # So we ONLY need to bubble `Acc` (L1).
    
    # Move Acc(L1) to Next(R1)? No, Next has code.
    # We need to swap Acc and Instr.
    # [Acc, Instr] -> [Instr, Acc].
    # Then move head to Next. Result: [Instr, Acc, Next].
    # Then Acc is at L(1) relative to new Head.
    
    # Swap Acc(L1) and Instr(P).
    # Use L(2) as temp (it is 0).
    L(1); B(); L(1); I(1); R(1); D(); C() # Move Acc to L2
    R(1); B(); L(2); I(1); R(2); D(); C() # Move Instr to L1
    L(2); B(); R(1); I(1); L(1); D(); C() # Move L2(Acc) to Instr
    
    # Now [Acc(was Instr), Instr(was Acc)].
    # Move Head Right.
    R(1)
    # New state: [OldHead, Acc, NewHead].
    # L(1) is Acc.
    # L(2) is OldHead (Previous Instr).
    # L(3) is ...
    # This maintains the invariant!
    
    C()
    
    DEBUG(69) # E

if __name__ == "__main__":
    main()
