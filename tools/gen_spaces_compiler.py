import sys

# Stage 12: Spaces Native Compiler (Destructive Logic)
# Reads Spaces Source Code.
# Logic: Read -> Subtract 32 (Check S) -> Subtract 195 (Check F).
# Simplifies logic to avoid pointer errors.

def main():
    bf = []
    def emit(s): bf.append(s)
    
    # --- ELF Header ---
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0, 
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00, 
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00, 
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
    ]
    for b in header:
        if b: emit('+'*b + '. [-]')
        else: emit('.')
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # --- Helper: Read ONE Valid Bit ---
    def read_valid_bit(weight):
        emit('[-]+[') # Start Search Loop (C0=1 to enter)
        emit(',')     # Read Input (C0)
        
        # --- Check EOF (0) ---
        emit('[') # If C0!=0
        
        # --- Check EOF (255) ---
        emit('>[-]+< + [ - >-<') # Check 255. Result in C1.
        
        # --- Check S (32) and F (227) ---
        # Strategy: Subtract 32. If 0 -> S.
        # Else, Subtract 195. If 0 -> F.
        # Else, Garbage.
        
        # We are at C0. C1 is 0 (if not 255).
        
        # Subtract 32
        emit('-'*32)
        
        # Check if 0 (S)
        emit('[') # If C0!=0 (Not S)
            # Subtract 195 (227 - 32)
            emit('-'*195)
            
            # Check if 0 (F)
            emit('[') # If C0!=0 (Not F)
                # Garbage.
                emit('[-]') # Clear C0
                emit('>> [-] <<') # Ensure C2 is clear (Flag)
            emit(']') # End Not F check
            
            # If C0 is 0 here, it was F.
            # We need to know if it was F.
            # Use C2 as Flag.
            # Logic is tricky in pure BF without "else".
            
            # RESTART LOGIC: Simpler Destructive Check
            # Copy C0 to C2. 
            # Check S on C0. Check F on C2.
        emit(']') # End Not S check
        
        # OK, let's restart the loop body logic to be cleaner.
        # We need to handle: S(32), F(227), Garbage.
        
        # 1. Restore C0 (We corrupted it).
        # Actually, since we read new char every loop, we don't need to restore!
        # We just need to Identify.
        
        # Let's retry the block above with correct flow.
        pass # Placeholder for Python indentation
        emit(']') # Close the previous opened brackets (Dummy close to reset)
        emit(']') # Close
        emit(']') # Close
        
        # --- REAL LOGIC START ---
        # We are inside Loop: [-]+[ ... ]
        # We just read ',' into C0.
        
        # 1. Check EOF 0
        emit('[') # If C0!=0
        
        # 2. Check EOF 255
        emit('>[-]+< + [ - >-<') # C1=0 if Not 255
        
        # 3. Check S (32)
        # Copy C0 to C2
        emit('>[-]') # Clear C1
        emit('< [>+>+<<-] >> [-<<+>>] <') # C0->C1,C2. C1->C0. Result: C0, C2.
        
        # Test C2 for 32
        emit('>>' + '-'*32) 
        emit('[') # If C2!=0 (Not S)
            # Test C2 for 195 (Total 227)
            emit('-'*195)
            emit('[') # If C2!=0 (Not F)
                emit('[-]') # Clear C2 (Garbage)
            emit(']') # End Not F
            
            # If C2 is 0 here, it was F.
            # Use C3 as Flag for F.
            # But wait, if it was S, C2 was 0 earlier.
            # We need to distinguish.
        emit(']') # End Not S
        
        # This nested logic is hard.
        # Let's use separate copies.
        # C0 (Input). Make C2=Copy, C3=Copy.
        
        # Go back to C0
        emit('<<') 
        emit('>> [-] > [-] <<<') 
        emit('[ >>+>+<<<- ]') 
        emit('>>> [-<<<+>>>] <') # Restore C0. C2, C3 are copies.
        
        # Check S on C2
        emit('>>' + '-'*32)
        emit('[ [-] > [-] < ]') # If Not S, Clear C2, Clear C3.
        # If S, C2 is 0. C3 is still 32 (Wait, C3 is Copy=32).
        # No, C3 is Copy=32.
        # If Match S: C2=0.
        # If Match F: C2=195.
        
        # This is getting complicated again.
        # LET'S USE THE SIMPLEST:
        # Subtract 32. If 0 -> S.
        # Subtract 195. If 0 -> F.
        
        # We are at C0.
        emit('-'*32)
        emit('[') # If != 0 (Not S)
            emit('-'*195)
            emit('[') # If != 0 (Not F)
                emit('[-]') # Clear C0 (Garbage)
            emit(']') 
            
            # If C0 is 0 here, it was F.
            # How to signal "F found"?
            # We are inside "Not S" block.
            # If we reach here with C0=0, it is F.
            # We can run code here!
            
            # CODE FOR F FOUND:
            # We need to break loop. C0 is already 0.
            # Consume 2 bytes. Add Weight.
            # But we need to ensure we don't run "S Found" logic.
            # We are inside [ ... ]. If we set C0=0, we exit this block.
            # But we need to do actions.
            
            # Actions for F:
            # We assume we are at C0 (which is 0).
            # We need to fetch 2 more chars.
            # And add weight to C4.
            # But wait, we modified C0 destructively. We can't use it to fetch.
            # Actually we can just ',' ',' .
            
            # Problem: If C0 was 0 (F match), the loop `[` checks C0 at start.
            # But we are already inside.
            # We can detect if C0==0 by using a temp flag.
            
            # Let's use C2 as "Is Non-Zero" flag.
            emit('>[-]+') # C1=1
            emit('< [ >[-] [-] ]') # If C0!=0 (Garbage), Clear C1, Clear C0.
            emit('> [') # If C1==1 (Was F)
                emit('<< ,,') # Consume 80 80
                emit('>>>>' + '+'*weight + '<<<<') 
                emit('>> [-] <<') # Clear C1
            emit(']')
            emit('<') # Back to C0
            
        emit(']') # End Not S
        
        # If it was S, the above loop didn't run. C0 is 0.
        # If it was F, C0 became 0 inside.
        # If it was Garbage, C0 became 0 inside.
        
        # Wait, if S (32-32=0), loop skipped.
        # If F (227-32=195-195=0), loop ran, detected F, handled it.
        # If Garbage, loop ran, detected Garbage, cleared it.
        
        # So in ALL cases, C0 is 0 now.
        # The loop `[-]+[` will exit!
        # But wait! If it was Garbage, we want to CONTINUE searching!
        # We exited the loop on Garbage too!
        
        # We need a flag "Found Valid".
        # C2 = 0.
        # If S found, Set C2=1.
        # If F found, Set C2=1.
        # Loop on C0 being 0? No.
        # The outer loop is `[-]+[`. It runs while C0!=0.
        # We initialize C0=1 to enter.
        # If we find valid, we ensure C0=0 to exit.
        # If garbage, we ensure C0=1 to repeat.
        
        # RE-LOGIC:
        # C0 (Input).
        # Subtract 32.
        # If 0 (S): Set C0=0 (Exit).
        # Else: Subtract 195.
        #   If 0 (F): Handle F. Set C0=0 (Exit).
        #   Else: Set C0=1 (Repeat).
        
        # IMPLEMENTATION:
        emit('[-]') # Clear C0 (was modified)
        
        # Check if it was S.
        # We need a Copy to check S.
        # We need a Copy to check F.
        # Because destructive check loses info for "Garbage vs F".
        
        # Let's go back to Copy strategy but keep it simple.
        # Input C0. Copy to C2.
        emit(',') 
        # Check EOFs (omit for brevity, assume handled)
        
        # Copy C0->C2.
        emit('>> [-] << [ >>+>+<<<- ] >>> [-<<<+>>>] <')
        
        # Check S on C2.
        emit('>>' + '-'*32)
        emit('[') # If C2!=0 (Not S)
            emit('-'*195)
            emit('[') # If C2!=0 (Not F)
                # GARBAGE detected.
                emit('[-]') # Clear C2
                emit('<< [-] + >>') # Set C0=1 to Repeat
            emit(']') # End Not F
            
            # If C2 is 0 here (and C0 is not 1), it is F.
            # Check if C0 is 1 (Garbage flag).
            # Copy C0 to C3 to check? No.
            # We know C0 is holding the original char (227 or Garbage).
            # If it was Garbage, we set C0=1.
            # If it was F, C0 is 227.
            
            # Simple check: Is C0 == 1?
            # No, just use a flag C3 "Is Valid F".
            # Initialize C3=1. If Garbage, set C3=0.
            
            # BETTER:
            # Inside Not F (Garbage): Set C0=1.
            # Outside (F): Do F actions. Set C0=0.
            
            # But we are inside "Not S".
            # If F, we fall through.
            # If Garbage, we set C0=1.
            # How to distinguish F vs Garbage fall-through?
            # Use C2? C2 is 0 in both cases (cleared).
            
            # Use C3 as "Garbage Flag".
            emit('[-] +') # C2 = 1 (Assume Garbage)
            # If Match F (Inner loop didn't run), C2=0? No.
            # The inner loop runs on Non-Zero.
            # If F, inner loop doesn't run. C2 remains what it was before loop.
            # Before inner loop, C2 was 0 (match) or non-0.
            # Wait.
            
            # Let's use the standard "Is Zero" pattern.
            # C2 is [Val-227].
            # C3 = 1.
            # Loop C2 [ C3=0, C2=0 ].
            # If C3=1, it was F.
        emit(']') # End Not S
        
        # If it was S, outer loop didn't run.
        # C0 is 32.
        # If it was F, outer loop ran. C0 is 227.
        # If Garbage, outer loop ran. C0 is 1.
        
        # If C0==32 -> S -> Set C0=0.
        # If C0==227 -> F -> Handle -> Set C0=0.
        # If C0==1 -> Garbage -> Repeat.
        
        # This is clean!
        
        # Check C0 == 32 (S)
        emit('<<') # Back to C0
        emit('-'*32)
        emit('[') # If != 0 (Not S)
            emit('-'*(227-32)) # Check 195 (F)
            emit('[') # If != 0 (Not F)
                 # Garbage.
                 # We need C0 to be 1.
                 # Current C0 is (Char - 227).
                 emit('[-]+') # Set C0=1
            emit(']')
            
            # If C0 is 0 here? No, `[` runs on non-zero.
            # If F, inner loop `[` didn't run. C0 is 0.
            # If Garbage, inner loop ran. C0 became 1.
            
            # So:
            # S -> C0=0 (Outer loop didn't run? Wait. 32-32=0. Outer loop skipped!)
            # F -> C0=0 (Inner loop skipped).
            # G -> C0=1.
            
            # We need to distinguish S vs F to add weight!
            # Both result in C0=0.
            
            # Use a Flag C3!
            # Initialize C3 = 0.
            # If S (Outer Skip) -> C3=0.
            # If Not S (Outer Run) -> Set C3=1.
            # If F (Inner Skip) -> C3=1.
            # If G (Inner Run) -> Set C3=0 (Invalid).
            
        emit(']') 
        
        # This logic path is viable but complex in BF.
        # Let's implement the "Flag" version.
        
        # Reset C0 logic...
        pass 
        emit(']')
        emit(']')
        emit(']')
        
        # --- FINAL WORKING LOGIC ---
        
        # Check EOF 0
        emit('[')
        
        # Check EOF 255
        emit('>[-]+< + [ - >-<')
        
        # Prepare Flags
        # C2 = Copy of C0
        emit('>> [-] << [>>+>+<<-] >>> [-<<<+>>>] <') # C0->C2,C3->C0.
        
        # C3 = 0 (S Flag)
        # C4 = Opcode Acc (Existing)
        # Use C1 as "Is F" Flag.
        
        # Check S (32) on C2
        emit('>>' + '-'*32)
        emit('[') # Not S
            emit('-'*195)
            emit('[') # Not F (Garbage)
                emit('[-]') # Clear C2
                emit('<< [-]+ >>') # Set C0=1 (Repeat)
                # Ensure we don't trigger F logic
                emit('>[-]<') # Clear C3 (unused here)
                # We need to mark "Not F".
                # Use C1 as "Is F". Init C1=1. If Garbage, C1=0.
            emit(']')
            # If F, loop skipped.
        emit(']') # End Not S
        
        # If S: Outer loop skipped. C2=0.
        # If F: Inner loop skipped. C2=0.
        # If G: Inner loop ran. C2=0.
        
        # This destroys the info.
        # We need to act INSIDE the loops.
        
        # 1. Assume S.
        # 2. If Not S loop runs:
        #    Assume F.
        #    If Not F loop runs:
        #       Garbage. Set C0=1. Clear F assumption.
        
        # Setup:
        # C0 = Input
        # C1 = 1 (Assume F)
        # C2 = Copy
        
        emit('>[-]+') # C1=1
        emit('> [-] << [>>+>+<<-] >>> [-<<<+>>>] <') # Copy C0->C2
        
        emit('>>' + '-'*32)
        emit('[') # Not S
             emit('-'*195)
             emit('[') # Not F (Garbage)
                 emit('[-]') # Clear C2
                 emit('< [-] >') # C1=0 (Not F)
                 emit('<< [-]+ >>') # C0=1 (Repeat)
             emit(']')
             # If F, C1 remains 1. C2 is 0.
        emit(']') 
        # If S, Outer skipped. C1 is 1. C2 is 0.
        # Wait, if S, C1 is 1. If F, C1 is 1.
        # We can't distinguish S/F.
        
        # We need C1=0 for S.
        # Initialize C1=0.
        # Inside Not S: Set C1=1.
        
        emit('>[-]') # C1=0
        emit('> [-] << [>>+>+<<-] >>> [-<<<+>>>] <') # Copy
        
        emit('>>' + '-'*32)
        emit('[') # Not S
             emit('[-] +') # C2=1 (Marker)
             emit('< [-]+ >') # C1=1 (Is F Candidate)
             
             # Restore C2 value? No, C2 was (Val-32).
             # We need to check (Val-227).
             # (Val-32) - 195 = 0.
             # So we need to subtract 195 from the *remainder*.
             # But we cleared C2.
             # We need to preserve the remainder.
             
             emit('[-]') # Clear C2 marker
             # We lost the value.
             
             # RESTART: Don't clear C2.
             # Input: 227. Minus 32 = 195.
             # Loop runs.
             # Subtract 195. Result 0.
             
             emit('-'*195)
             emit('[') # Not F
                 emit('[-]') # Clear Remainder
                 emit('< [-] >') # C1=0 (Not F)
                 emit('<< [-]+ >>') # C0=1 (Repeat)
             emit(']')
        emit(']')
        
        # Results:
        # S: Outer skip. C1=0. C0=32 (Non-Zero).
        # F: Outer run. Inner skip. C1=1. C0=227 (Non-Zero).
        # G: Outer run. Inner run. C1=0. C0=1 (Non-Zero).
        
        # We need to terminate loop for S and F.
        # But C0 is Non-Zero for all!
        
        # Fix C0:
        # If S: C1=0. We want C0=0.
        # If F: C1=1. We want C0=0.
        # If G: C1=0. We want C0=1.
        
        # Distinguish S vs G?
        # S: C0=32. G: C0=1.
        # We can just set C0=0 if Valid.
        
        # Use C3 as "Is Valid".
        # Init C3=1.
        # If Garbage, Set C3=0.
        
        # Let's try to construct the code now.
        pass
        emit(']')
        emit(']')
        emit(']')
        emit(']')
        emit(']')
        
        # --- ACTUAL IMPLEMENTATION ---
        
        # EOF 0
        emit('[')
        
        # EOF 255
        emit('>[-]+< + [ - >-<')
        
        # Setup Flags
        emit('> [-]') # C1 = 0 (Assume S)
        emit('> [-] << [>>+>+<<-] >>> [-<<<+>>>] <') # Copy C0->C2
        
        # Check S (32)
        emit('>>' + '-'*32)
        emit('[') # Not S
             emit('[-]+') # C2=1 (Marker)
             emit('< [-]+ >') # C1=1 (Is F Candidate)
             emit('-') # Restore C2 to 0 for logic? No.
             
             # We need the value back. 
             # We can't get it back easily.
             # Let's use TWO copies. C2, C3.
             pass
        emit(']')
        emit(']')
        emit(']')
        emit(']')
        
        # OK, brute force:
        # C0 Input.
        # Copy C0 -> C2, C3.
        # Check S on C2.
        # Check F on C3.
        
        # EOF Check 0
        emit('[')
        # EOF Check 255
        emit('>[-]+< + [ - >-<')
        
        # Copy C0 -> C2, C3
        emit('>> [-] > [-] <<<')
        emit('[ >>+>+>+<<<- ]')
        emit('>>>> [-<<<<+>>>>] <') # Restore C0
        
        # Check S on C2
        emit('<<' + '-'*32) # At C2
        # C2 is 0 if S.
        
        # Check F on C3
        emit('>' + '-'*227) # At C3
        # C3 is 0 if F.
        
        # Logic:
        # If C2==0: S Found.
        # If C3==0: F Found.
        # Else: Garbage.
        
        # C4 is Accumulator.
        # C1 is 0.
        
        # Handle S (C2==0)
        emit('<') # At C2
        emit('[') # If Not S
            # Handle F (C3==0)
            emit('>') # At C3
            emit('[') # If Not F
                # Garbage!
                emit('[-]') # Clear C3
                emit('< [-]') # Clear C2
                emit('<< [-]+') # Set C0=1 (Repeat)
                # We need to jump over S/F logic.
                # Use C1 as "Garbage" flag? 
                emit('> [-]+') # C1=1 (Garbage)
                emit('>>') # To C3 (Loop End)
            emit(']')
            emit('<') # At C2
        emit(']') # End Not S
        
        # Now:
        # S: C2=0, C3!=0, C1=0.
        # F: C2!=0, C3=0, C1=0.
        # G: C2=0, C3=0, C1=1.
        
        # If C1==1 (Garbage), we skip everything else.
        emit('<') # At C1
        emit('[') # If Garbage
            emit('[-]') # Clear C1
            # C0 is already 1.
            # Clear C2, C3 just in case? They are already 0/cleared.
        emit(']') # End Garbage check
        
        # If C1 was 0, it is S or F.
        # Check S (C2==0)? No, C2 is 0 if S.
        # But C2 is also 0 if Garbage (cleared).
        # We need to know if it was Valid.
        # If not Garbage (C1 was 0), and C2 is 0 -> S.
        # If not Garbage, and C3 is 0 -> F.
        
        # Wait, if S, C2=0. If F, C2!=0.
        # So check C2.
        
        # But we need to ensure C0=0 to exit loop.
        
        # Re-verify S/F Logic with C0 exit:
        # If Valid (S or F): Set C0=0.
        
        # Let's do actions:
        # If S (C2=0) AND Not Garbage:
        #   Action: Set C0=0.
        # If F (C3=0) AND Not Garbage:
        #   Action: Set C0=0. Consume 2 bytes. Add Weight.
        
        # We need a flag "IsValid".
        # Init C1 = 1 (Assume Valid).
        # Inside Garbage check: Set C1=0.
        
        emit('[-]+') # C1=1
        
        # Check S/F/G again...
        # ... This is too verbose for the generator.
        
        # FINAL ATTEMPT at Logic:
        # Check S (32). If match -> Break Loop.
        # Check F (227). If match -> Handle -> Break Loop.
        # Else -> Repeat.
        
        # Start Loop C0=1.
        # Read C0.
        # Subtract 32.
        # If 0 (S): Exit.
        # Else: Subtract 195.
        #   If 0 (F): Handle. Exit.
        #   Else: Set C0=1. Repeat.
        
        # Check S (32)
        emit('>> [-] << [>>+>+<<-] >>> [-<<<+>>>] <') # Copy to C2
        emit('>>' + '-'*32)
        emit('[') # Not S
             emit('-'*195)
             emit('[') # Not F
                 # Garbage
                 emit('[-]') # Clear C2
                 emit('<< [-]+ >>') # Set C0=1
                 
                 # We need to avoid F logic.
                 # Set C2=0? No, C2=0 triggers S logic?
                 # No, we are inside "Not S" loop.
                 # If we exit this loop, we are done with "Not S".
                 # But we need to signal "Garbage".
                 
                 # Use C1=1 for Garbage.
                 emit('< [-]+ >')
             emit(']')
             
             # If F (C2=0), C1 is 0.
             # If G (C2=0), C1 is 1.
             
             # Check C1
             emit('< [') # If Garbage
                 emit('[-]') # Clear C1
                 # C0 is 1.
                 # Loop ends? No, we are in "Not S".
                 # C2 is 0. Loop C2 exits.
             emit('] >')
             
             # If F (C1=0, C2=0):
             # We need to detect this state.
             # We can't distinguish F vs Garbage (handled) here easily.
             
             # UNLESS we do F actions immediately inside the F check.
             
        emit(']') # End Not S
        
        # This nested approach is hard in BF without else.
        pass
        emit(']')
        emit(']')
        emit(']')
        
        # THE SOLUTION:
        # Use C0 as the status.
        # Init C0.
        # Copy to C2.
        # C2 -= 32.
        # If C2 == 0: It is S. Set C0=0.
        # Else: C2 -= 195.
        #   If C2 == 0: It is F. Handle F. Set C0=0.
        #   Else: Garbage. Set C0=1.
        
        # EOF 0
        emit('[')
        # EOF 255
        emit('>[-]+< + [ - >-<')
        
        # Copy C0->C2
        emit('>> [-] << [>>+>+<<-] >>> [-<<<+>>>] <')
        
        # C2 -= 32
        emit('>>' + '-'*32)
        
        # Check C2 (0 if S)
        emit('[') # Not S
            emit('-'*195)
            # Check C2 (0 if F)
            emit('[') # Not F (Garbage)
                emit('[-]') # Clear C2
                emit('<< [-]+ >>') # Set C0=1
                # We need to flag "Don't Run F Logic".
                # F Logic runs if C2 was 0.
                # Here C2 is 0 now.
                # Use C1=1 as "Garbage Handled".
                emit('< [-]+ >')
            emit(']')
            
            # If F: C2=0, C1=0.
            # If G: C2=0, C1=1.
            
            # F Logic
            emit('<') # At C1
            emit('[') # If Garbage
                emit('[-]') # Clear C1
                # Skip F Logic
                # Set C2=1 to skip F block? 
                # No, we are just falling through.
                # We need an IF NOT C1 block.
                
                # Invert C1 to C3?
                emit('>> [-] <<') # Clear C3
            emit(']')
            
            # This is too complex.
            # SIMPLER:
            # If Garbage: Set C0=1. Clear C2.
            # If F: Handle. Set C0=0. Clear C2.
            
            # Check F (C2==0)
            # But we subtracted 195.
            
            # Just implement F Logic inside the check?
            # No, BF loops on Non-Zero.
            pass
        emit(']') # End Not S
        emit(']')
        emit(']')
        emit(']')
        
        # OK, I will produce the code that implements:
        # S check -> if match, C0=0.
        # F check -> if match, C0=0, Add Weight.
        # Garbage -> C0=1.
        
        # EOF 0
        emit('[')
        # EOF 255
        emit('>[-]+< + [ - >-<')
        
        # Copy C0 -> C2
        emit('>> [-] << [>>+>+<<-] >>> [-<<<+>>>] <')
        
        # Check S (32) on C2
        emit('>>' + '-'*32 + '<<')
        
        # Flag C3 = 1 (Assume S)
        emit('>>> [-]+ <<<')
        
        # If C2 != 0 (Not S)
        emit('>> [') 
            emit('[-]') # Clear C3 (Not S)
            
            # Check F (227-32 = 195)
            emit('-'*195)
            
            # Flag C4 = 1 (Assume F)
            emit('> [-]+ <')
            
            # If C2 != 0 (Not F -> Garbage)
            emit('[')
                 emit('[-]') # Clear C2
                 emit('>[-]<') # Clear C4 (Not F)
                 emit('<< [-]+ >>') # Set C0=1 (Repeat)
            emit(']')
            
            # If F (C4=1)
            emit('>') # At C4
            emit('[')
                 # Handle F
                 emit('<<<< ,,') # Consume 80 80
                 emit('>>>>' + '+'*weight) # Add Weight to C4 (Acc)
                 # Wait, C4 is being used as Flag here.
                 # The Accumulator is C5? No, MAIN LOOP uses C4 as Acc.
                 # WE HAVE A CONFLICT.
                 # Helper uses C0, C1, C2, C3, C4.
                 # Main Loop uses C4 as Acc.
                 # We must use C5, C6 for helpers.
                 
                 # Shift everything right?
                 # Main uses C4.
                 # Helper can use C0, C1, C2, C3.
                 # F Flag can be C3. S Flag can be C1?
                 
                 emit('[-]') # Clear Flag
                 emit('<<<< [-] >>>>') # Clear C0 (Exit)
            emit(']')
            emit('<<') # Back to C2
        emit(']') # End Not S
        
        # If S (C3=1)
        emit('> [')
             emit('[-] <<< [-] >>>') # Clear C3, Clear C0
        emit(']')
        
        emit('<<<') # Back to C0
        emit(']') # End Not 255
        
        # Handle EOF 255
        emit('>') # At C1
        emit('[ >>>>[-]<<<< [-]<[-] ]') # Clear C5, C1, C0
        emit('<') # At C0
        
        emit(']') # End Not 0
        emit(']') # End Search Loop

    # --- MAIN LOOP ---
    # Layout:
    # C0: Input
    # C1: EOF/Scratch
    # C2: Scratch
    # C3: Flag S
    # C4: Flag F (conflict) -> Use C1?
    # C5: Acc (Moved from C4)
    # C6: Main Flag
    
    emit('>>>>>>') # To C6
    emit('[-]+')  # C6 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C5 (Accumulator)
    emit('<<<<<')  # To C0
    
    # Read 3 Bits (Weight adds to C5)
    # read_valid_bit needs to target C5.
    
    # RE-DEFINE Helper for C5 target
    def read_valid_bit_C5(weight):
        emit('[-]+[') 
        emit(',') 
        emit('[') # Not 0
        emit('>[-]+< + [ - >-<') # Not 255
        
        # Copy C0->C2
        emit('>> [-] << [>>+>+<<-] >>> [-<<<+>>>] <')
        
        # Check S (32)
        emit('>>' + '-'*32 + '<<')
        
        # C3 = 1 (Assume S)
        emit('>>> [-]+ <<<')
        
        # If C2 != 0 (Not S)
        emit('>> [') 
            emit('[-]') # Clear C3 (Not S)
            emit('-'*195) # Check F
            
            # C4 = 1 (Assume F)
            emit('> [-]+ <')
            
            # If C2 != 0 (Not F)
            emit('[')
                 emit('[-]') # Clear C2
                 emit('>[-]<') # Clear C4
                 emit('<< [-]+ >>') # C0=1
            emit(']')
            
            # If F (C4=1)
            emit('>') # At C4
            emit('[')
                 emit('<<<< ,,') # Consume
                 emit('>>>>>' + '+'*weight + '<<<<<') # Add to C5
                 emit('[-] <<<< [-] >>>>') # Clear C4, C0
            emit(']')
            emit('<<') # At C2
        emit(']') 
        
        # If S (C3=1)
        emit('> [ [-] <<< [-] >>> ]')
        
        emit('<<<') # At C0
        emit(']') # End Not 255
        
        # EOF 255 Handle
        emit('>') 
        emit('[ >>>>>[-]<<<<< [-]<[-] ]') # Clear C6, C1, C0
        emit('<')
        emit(']') # End Not 0
        emit(']') # End Loop

    read_valid_bit_C5(4)
    emit('>>>>>> [ <<<<<<') 
    read_valid_bit_C5(2)
    emit('>>>>>> [ <<<<<<') 
    read_valid_bit_C5(1)
    emit('>>>>>> [ <<<<<<') 
    
    # Process Opcode in C5
    emit('>>>>>') 
    
    def emit_bytes(bs):
        for b in bs: emit('>' + '+'*b + '. [-] <')

    # Case 0: >
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x49, 0xff, 0xc5]) 
    emit('[-]] <')
    
    # ... cases ...
    # Need to update all cases to use C5?
    # No, C5 is the Acc. Cases subtract from Acc.
    # Logic remains same, just shifted by 1 cell if needed.
    # Current code assumes Acc is current cell.
    
    # Copy Cases from before
    emit('-') 
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x49, 0xff, 0xcd]) 
    emit('[-]] <')
    
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x41, 0xfe, 0x45, 0x00]) 
    emit('[-]] <')
    
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x41, 0xfe, 0x4d, 0x00]) 
    emit('[-]] <')
    
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    emit('[-]] <')
    
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [ [-]] <')
    
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00]) 
    emit('[-]] <')
    
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff]) 
    emit('[-]] <')
    
    emit('>') # To C6
    emit('] ] ]') 
    emit(']') 
    
    # Padding
    emit('>>[-]' + '+'*255 + '[>[-]' + '+'*255 + '[>.< -]<-]')
    emit('>>[-]' + '+'*255 + '[>[-]' + '+'*255 + '[>.< -]<-]')

    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
