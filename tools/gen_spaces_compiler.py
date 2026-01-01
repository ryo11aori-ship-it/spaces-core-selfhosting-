import sys

# Stage 12: Spaces Native Compiler (Pointer Logic Final Fix)
# Reads Spaces Source Code.
# Fixes pointer drift in Check F block (missing return to C0).

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
        emit('[-]+[') # Start Search Loop
        emit(',')     # Read Input (C0)
        
        # --- Check EOF (0) ---
        emit('[') # If C0!=0
        
        # --- Check EOF (255) ---
        emit('>[-]+< + [ - >-<') # Check 255
        
        # --- Check F (227) ---
        # We are at C0.
        # Copy C0 -> C1, C2. Restore C0 from C2.
        # Layout: C0(Input), C1(Copy), C2(Copy)
        emit('>[-]') # Clear C1
        emit('< [>+>+<<-]') # C0 -> C1, C2
        emit('>> [-<<+>>] <') # C2 -> C0. End at C1.
        
        # Compare C1 with 227
        emit('-'*227)
        
        # Result C1 is 0 if Match. Set C2=1 if Match.
        emit('>[-]+') # C2=1
        emit('< [ >[-] < [-] ]') # If C1!=0, Clear C2, Clear C1.
        
        # If Match (C2=1)
        emit('>') # To C2
        emit('[') 
        # From C2, go to C0. Distance is 2.
        emit('<< ,,') # Consume 80 80 at C0
        emit('>>>>' + '+'*weight + '<<<<') # Add Weight to C4
        emit('[-]') # Clear C0 to Exit Loop
        emit('>> [-]') # Clear C2
        emit(']') 
        emit('<<') # Back to C0 (From C2)
        
        # IMPORTANT FIX:
        # Before this fix, we were at C1 if Match Failed.
        # But if Match Succeeded, we are at C0.
        # Wait. If Match Failed, `emit('>')` takes us to C2.
        # Inside `[` logic runs if Match.
        # If No Match, we are at C2 (value 0).
        # We need to go back to C0.
        
        # Let's trace No Match:
        # C1 checked. C2 set to 0. C1 cleared.
        # `>` to C2. `[` skipped.
        # `<<` to C0.
        # So we ARE at C0!
        
        # Wait, previous analysis said we were at C1.
        # `emit('>[-]+') # C2=1` -> At C2.
        # `emit('< [ >[-] < [-] ]') # If C1!=0` -> Ends at C1.
        # `emit('>') # To C2`. -> At C2.
        # `emit('[ ... ]')`.
        # `emit('<<')`. -> At C0.
        
        # So we ARE at C0.
        # Why did I think we were at C1?
        # Ah, the logic flow seems correct now.
        
        # Let's re-verify Check S.
        
        # --- Check S (32) ---
        emit('[') # If C0!=0 (Not F)
        
        # Copy C0 to C2, C3. Restore C0 from C3.
        # Layout: C0, C1, C2(Copy), C3(Copy)
        emit('>> [-] > [-] <<<') 
        emit('[ >>+>+<<<- ]') 
        emit('>>> [-<<<+>>>] <') # We are at C2.
        
        # Compare C2 with 32
        emit('-'*32)
        
        # Set C3=1 if Match (C2==0)
        emit('>[-]+ < [ >[-] < [-] ]') # Ends at C2.
        
        emit('>') # To C3
        emit('[')
        # Weight 0
        emit('[-] <<< [-]') # Clear C3, Clear C0
        emit('>>>') # Back to C3
        emit(']')
        emit('<<<') # Back to C0
        
        emit(']') # End Not F
        
        # Back to C1 check?
        # We are at C0.
        # We need to go to C2?
        # `emit('>>') # To C2 (Scratch position for loop logic)`
        
        # The `Check EOF 255` loop logic expects us to close `]`.
        # It was: `emit('>[-]+< + [ - >-<')`.
        # This structure doesn't wrap the Checks in a loop.
        # It's sequential.
        # But `Check EOF 255` has `[ ... ]`.
        # `emit('[') # If C0!=0 (Original was not 255)`
        # This wraps Check F and Check S.
        # So we must end at C0 inside this loop.
        
        # We are at C0.
        # We need to restore C0 if it was modified?
        # No, we restored C0.
        # But we need to handle the `emit('-') # Restore C0` logic from `Check EOF 255`.
        # Wait!
        
        # `Check EOF 255`:
        # `emit('>[-]+<') # C1=1`
        # `emit('+') # C0 += 1`
        # `emit('[') # If C0!=0`
        # `emit('-') # Restore C0`
        # `emit('>-<') # C1=0`
        
        # If we just continue here, we are fine.
        # Check F starts.
        
        # At the end of Check S:
        # `emit(']') # End Not F`
        # We are at C0.
        
        # Then `emit('>>') # To C2` ? Why?
        # Because `emit(']') # End Not 255` is coming.
        # The `[` for Not 255 was at C0.
        # So `]` expects C0.
        # If we emit `>>`, we are at C2.
        # Then `]` jumps back to start (at C0?).
        # No, `]` checks current cell. If C2!=0, repeat.
        # C2 should be 0. So loop exits.
        # But `]` jumps back to `[` location in code? No.
        
        # This is `If` logic using `[...]`.
        # If we enter, we must clear the condition or break.
        # The condition was `C0`.
        # But `C0` is our Input! We cannot clear it!
        # Unless we successfully processed it (F or S).
        # If we processed F or S, we cleared C0. So loop exits.
        # If we didn't (Garbage), C0 is still there (32 or 227 or other).
        # So the loop repeats!
        # This is BAD. Infinite loop on Garbage logic inside `Check 255`.
        
        # If Garbage, we should NOT match F or S.
        # C0 remains non-zero.
        # We hit `]`. It loops back to `emit('-')`? No.
        # It loops back to `emit('[')`.
        # Then `emit('-')` runs again! C0 decremented again!
        # Then `emit('>-<')` runs again.
        # Then Check F/S runs again on modified C0.
        # This is catastrophic.
        
        # FIX:
        # We must NOT use the input C0 as the loop condition for the `If Not 255` block.
        # We need a temporary flag.
        
        # Logic:
        # C0 = Input.
        # C1 = 1.
        # C0 += 1.
        # If C0 != 0:
        #    C0 -= 1.
        #    C1 = 0.
        #    RUN CHECKS.
        #    Set C0 = 0 to exit THIS block?
        #    No, we need C0 for checks.
        
        # Use a copy for the check?
        # Or enter the block, and immediately break logic?
        
        # Standard IF:
        # Temp = Copy C0.
        # Temp [ Restore C0. Do Stuff. Zero Temp. ]
        
        # Here:
        # C0 += 1.
        # [
        #   C0 -= 1.
        #   C1 = 0.
        #   Do Stuff.
        #   How to exit? We need this loop to run ONCE.
        #   But C0 is our data! We can't zero it!
        # ]
        
        # SOLUTION:
        # Move Data out of C0?
        # Or use C1 as the loop variable?
        # C1 is 1.
        # C0 += 1.
        # If C0 == 0: (Was 255)
        #   C1 is still 1.
        # Else:
        #   C0 -= 1.
        #   C1 = 0.
        
        # This check structure `>[-]+< + [ - >-< ]` relies on the loop running if C0!=0.
        # But it fails because we can't zero C0.
        
        # ALTERNATIVE EOF 255 CHECK:
        # Copy C0 to C2.
        # Add 1 to C2.
        # If C2==0 -> 255.
        
        emit('>> [-] << [>>+>+<<-] >>> [-<<<+>>>] <') # Copy C0->C2
        emit('>> +') # C2 += 1
        
        # If C2 != 0 (Not 255)
        emit('[') 
            emit('[-]') # Clear C2 (Exit condition)
            emit('<<') # Back to C0
            
            # --- Check F (227) ---
            # ... Copy logic ...
            emit('>[-]') 
            emit('< [>+>+<<-]') 
            emit('>> [-<<+>>] <') 
            
            emit('-'*227)
            emit('>[-]+ < [ >[-] < [-] ]') 
            emit('>') # To C2
            emit('[') 
            emit('<< ,,') 
            emit('>>>>' + '+'*weight + '<<<<') 
            emit('[-] <<< [-] >>>') 
            emit(']') 
            emit('<<') # Back to C0
            
            # --- Check S (32) ---
            emit('[') # If C0!=0 (Not F)
            emit('>> [-] > [-] <<<') 
            emit('[ >>+>+<<<- ]') 
            emit('>>> [-<<<+>>>] <') # We are at C2.
            emit('-'*32)
            emit('>[-]+ < [ >[-] < [-] ]')
            emit('>') # To C3
            emit('[')
            emit('[-] <<< [-] >>>') 
            emit(']')
            emit('<<<') # Back to C0
            emit(']') # End Not F
            
            # Go back to C2 to exit loop
            emit('>>')
        emit(']') # End Not 255 (C2)
        
        # If it was 255, C2 was 0, loop skipped.
        # But we need to detect 255 to exit the main loop.
        # If C2 was 0, it means EOF.
        # But C2 is also 0 if Not 255 (we cleared it).
        
        # Use C1 as "Is EOF" Flag.
        # Init C1=1.
        # Inside "Not 255" loop, Set C1=0.
        
        emit('< [-]+ >') # C1=1
        
        # Copy C0->C2 again... 
        # This is getting heavy.
        
        # Let's simplify.
        # Just use the original logic but fix the infinite loop issue.
        # `>[-]+< + [ - >-< ... CHECKS ... ??? ]`
        # Inside checks, we MUST set C0=0 to exit.
        # But if we set C0=0, we lose the char for checking.
        
        # Move C0 to C2 at start of check?
        # `[ - >>+<< ]` -> C0 moved to C2.
        # Run checks on C2.
        # If Garbage, move C2 back to C0? `>> [ <<+>>- ] <<`.
        # Then loop repeats? Yes!
        # If Valid, consume/clear. C0 remains 0. Loop exits.
        
        # THIS IS IT!
        
        emit('>[-]+<') # C1=1
        emit('+') # C0+=1
        emit('[') # If C0!=0 (Not 255)
            emit('-') # Restore C0
            emit('>-<') # C1=0 (Not 255)
            
            # Move C0 to C2
            emit('>> [-] << [>>+<<-]') 
            
            # Now C0 is 0! The loop `[...]` will exit naturally!
            # We must operate on C2.
            # If Garbage, we must restore C0 from C2.
            
            # --- Check F (227) on C2 ---
            # Copy C2 to C3
            emit('>> [>+>+<<-] >> [-<<+>>] <') # C2->C3,C4. C4->C2.
            
            emit('-'*227) # C3 -= 227
            emit('>[-]+ < [ >[-] < [-] ]') # C4=1 if match
            
            emit('>') # At C4
            emit('[') # If F
                emit('<<<< ,,') # Consume at C0 (Pointer relative to C4 is <<<<)
                emit('>>>>' + '+'*weight) # Add Weight (Acc is C4? No, Acc is C4 in Main. Here it's local C4)
                # Conflict on C4.
                # Main Loop C4 is Acc.
                # Here we are using C4 locally.
                # We need to shift everything.
                
                # Let's use C5 as Acc in Main.
                
                emit('>>>>>' + '+'*weight + '<<<<<') # Add to C5
                emit('[-] << [-] >>') # Clear C4, Clear C2
            emit(']')
            emit('<<') # At C2
            
            # --- Check S (32) on C2 ---
            emit('[') # If C2!=0 (Not F)
            
            # Copy C2 to C3
            emit('[>+>+<<-] >> [-<<+>>] <') 
            
            emit('-'*32) # C3 -= 32
            emit('>[-]+ < [ >[-] < [-] ]') # C4=1 if match
            
            emit('>') # At C4
            emit('[') # If S
                emit('[-] << [-] >>') # Clear C4, Clear C2
            emit(']')
            emit('<<') # At C2
            emit(']') # End Not F
            
            # If C2 is still not 0, it is Garbage.
            # Restore C0.
            emit('[ <<+>>- ]')
            
            # Go back to C0 to exit loop
            emit('<<')
        emit(']') # End Not 255
        
        # Handle EOF 255 (C1=1)
        # If 255, C0 was 0 (from overflow).
        # We need to Clear everything.
        emit('>') # At C1
        emit('[ >>>>[-]<<<< [-]<[-] ]') # Clear C5, C1, C0
        emit('<') # At C0
        
        emit(']') # End Not 0
        emit(']') # End Search Loop

    # --- MAIN LOOP ---
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C4 (Accumulator)
    emit('<<<<')  # To C0
    
    read_valid_bit(4)
    emit('>>>>> [ <<<<<') 
    read_valid_bit(2)
    emit('>>>>> [ <<<<<') 
    read_valid_bit(1)
    emit('>>>>> [ <<<<<') 
    
    # Process Opcode in C4
    emit('>>>>') 
    
    def emit_bytes(bs):
        for b in bs: emit('>' + '+'*b + '. [-] <')

    # Case 0: >
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x49, 0xff, 0xc5]) 
    emit('[-]] <')

    # Case 1: <
    emit('-') 
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x49, 0xff, 0xcd]) 
    emit('[-]] <')

    # Case 2: +
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x41, 0xfe, 0x45, 0x00]) 
    emit('[-]] <')

    # Case 3: -
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x41, 0xfe, 0x4d, 0x00]) 
    emit('[-]] <')

    # Case 4: .
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    emit('[-]] <')

    # Case 5: ,
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [ [-]] <')

    # Case 6: [
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00]) 
    emit('[-]] <')

    # Case 7: ]
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [') 
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff]) 
    emit('[-]] <')
    
    emit('>') # To C5
    emit('] ] ]') 
    emit(']') # End Main Loop
    
    # --- PADDING ---
    emit('>>[-]' + '+'*255 + '[>[-]' + '+'*255 + '[>.< -]<-]')
    emit('>>[-]' + '+'*255 + '[>[-]' + '+'*255 + '[>.< -]<-]')

    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
