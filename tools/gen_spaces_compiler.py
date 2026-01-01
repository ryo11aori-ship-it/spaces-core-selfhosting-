import sys

# Stage 12: Spaces Native Compiler (Flag Logic & Flat Indentation)
# Reads Spaces Source Code.
# Logic: Read -> Identify -> Set Flag -> Exit Loop -> Process Flag.
# Prevents Indentation Errors and Pointer Underflows.

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
        # C0: Input
        # C1: Copy/Scratch
        # C2: Flag S (Found)
        # C3: Flag F (Found)
        
        # Start Search Loop (C0=1 to enter)
        emit('[-]+[') 
        emit(',') # Read C0
        
        # Check EOF 0: If C0 is 0, loop exits automatically.
        # But we need to check 255 (-1).
        
        emit('[') # If C0 != 0
        
        # Check 255
        emit('>[-]+<') # C1=1
        emit('+') # C0 += 1
        emit('[') # If C0!=0 (Not 255)
        emit('-') # Restore C0
        emit('>-<') # C1=0 (Not 255)
        
        # Copy C0 to C1
        emit('>[-]') 
        emit('< [>+>+<<-] >> [-<<+>>] <') # C0->C1,C?->C0
        
        # Check S (32) on C1
        emit('>' + '-'*32)
        emit('[') # If C1 != 0 (Not S)
            
            # Check F (227) on C1
            # 227 - 32 = 195
            emit('-'*195)
            emit('[') # If C1 != 0 (Not F)
                # Garbage. C1 is non-zero.
                emit('[-]') # Clear C1
            emit(']') # End Not F
            
            # If C1 was 0 (Match F)
            # We are at C1.
            # We need to detect if it was F.
            # We assume it was F if we are here? No, loop runs if NonZero.
            # So if Match F, loop skipped.
            # If Garbage, loop ran and cleared C1.
            # So C1 is 0 in both cases.
            
            # We need to set Flag C3 if F.
            # Use "Else" pattern.
            # Set C3=1. If Garbage loop runs, Set C3=0.
            
            emit('>> [-]+ <<') # C3=1 (Assume F)
            # We need to redo the check or logic?
            # No, standard pattern:
            #   Set Flag.
            #   Check Cond. If Cond, Clear Flag.
            
            # But we destroyed the value.
            # Let's restart copy logic for simplicity.
            
        emit(']') # End Not S
        emit(']') # End Not 255
        emit(']') # End Not 0 (or Garbage continue)
        
        # The above logic was too complex for flat indentation.
        # SIMPLIFIED LINEAR LOGIC:
        
        # Reset Loop
        emit('[-]') # Clear C0
        emit('[-]+[') # Loop start
        emit(',') # Read
        
        # 1. Check EOF 0
        emit('[') # C0 != 0
        
        # 2. Check EOF 255
        emit('>[-]+< + [ - >-< ]') # C1=1 if 255. C0 restored.
        emit('>') # To C1
        emit('[') # If 255
        emit('[-] < [-] >') # Clear C1, Clear C0 (Exit)
        emit(']')
        emit('<') # To C0
        
        # 3. Check S (32)
        # Copy C0 -> C1
        emit('>>[-]<< [>>+>+<<<-] >>>[-<<<+>>>] <<')
        
        emit('>' + '-'*32) # C1 -= 32
        emit('[') # Not S
            
            # 4. Check F (195 more)
            emit('-'*195) # C1 -= 195
            emit('[') # Not F (Garbage)
                emit('[-]') # Clear C1
                # It is Garbage. C0 is still Non-Zero.
                # Loop will repeat.
            emit(']')
            
            # If F (C1 is 0 now):
            # We need to set Flag C3=1 and Clear C0 to Exit.
            # Use C2 as "Is F" candidate.
            # If Garbage loop ran, C1 was cleared.
            # If F, C1 became 0.
            # Indistinguishable here.
            
            # PRE-SET FLAG STRATEGY:
            # Set C3=1 (Assume F).
            # If Garbage loop runs, Set C3=0.
            
            emit('>> [-]+ <<') # C3=1
            
            # But we need C1 value for the Garbage loop condition.
            # We lost it because `[` consumes it? No, `[` checks it.
            # Inside `[`, we clear it.
            # We need to hook into the loop.
            
        emit(']') # End Not S
        
        # Okay, the cleanest "Flat" logic that works:
        
        emit('[-]') # Reset C0
        emit('[-]+[') # Start Loop
        emit(',') # Read C0
        
        # Check EOF 0
        emit('[') 
        
        # Check EOF 255
        emit('>[-]+< + [ - >-< ] > [ [-] < [-] > ] <')
        
        # Copy C0 to C1
        emit('>>[-]<< [>>+>+<<<-] >>>[-<<<+>>>] <<')
        
        # Assume S found (C2=1)
        emit('>> [-]+ <<') 
        
        # Check S
        emit('>' + '-'*32)
        emit('[') # Not S
            emit('[-] > [-] <') # Clear C1, Clear C2 (Not S)
            
            # Restore C1 from C0 (re-copy)
            emit('< [>+>+<<-] >> [-<<+>>] <')
            
            # Assume F found (C3=1)
            emit('>> [-]+ <<') 
            
            # Check F
            emit('-'*227)
            emit('[') # Not F (Garbage)
                emit('[-] >> [-] <<') # Clear C1, Clear C3 (Not F)
            emit(']')
        emit(']') 
        
        # Evaluate Flags.
        # If C2=1 (S): Clear C0 to Exit.
        # If C3=1 (F): Clear C0 to Exit.
        
        emit('>>') # To C2 (S Flag)
        emit('[') # If S
            emit('[-] << [-] >>') # Clear C2, Clear C0
        emit(']')
        
        emit('>') # To C3 (F Flag)
        emit('[') # If F
            emit('[-] <<< [-] >>>') # Clear C3, Clear C0
        emit(']')
        
        emit('<<<') # Back to C0
        emit(']') # End Not 0
        
        # If Garbage, C0 is still Non-Zero -> Loop Repeats.
        # If EOF/S/F, C0 is 0 -> Loop Exits.
        emit(']') # End Search Loop
        
        # --- POST LOOP ACTION ---
        # Flags C2(S) and C3(F) are cleared.
        # But we need to know IF it was F to add weight.
        # We need a Persistent Flag for the "Action" phase.
        # Let's use C2/C3 as the persistent flags?
        # But we cleared them to exit loop?
        # No, we cleared them INSIDE the loop logic.
        # We need them OUTSIDE.
        
        # Mod: Don't clear Flags to exit. 
        # Use Flags to clear C0, but keep Flags.
        
        # BUT: The logic above clears C0 if Flags are set.
        # If we keep flags, we can check them now.
        
        # RE-WRITE LOOP EXIT:
        # C2 is S Flag. C3 is F Flag.
        # Go to C2. If 1, Clear C0.
        # Go to C3. If 1, Clear C0.
        
        # C2/C3 will be 1 if found.
        # If Garbage, both 0.
        # If EOF, both 0.
        
        # So after loop:
        # If C3 is 1 (F): Consume 2 bytes, Add Weight.
        # If C2 is 1 (S): Do nothing (Weight 0).
        # Clear Flags.
        
        # Need to fix the logic above to NOT clear flags when exiting.
        # Just clear C0.
        
        pass # Just for mental break
        
    # --- FINAL READ_BIT IMPLEMENTATION ---
    def read_valid_bit_fixed(weight):
        emit('[-]+[') 
        emit(',') 
        emit('[') # C0!=0
        
        # 255 Check
        emit('>[-]+< + [ - >-< ] > [ [-] < [-] > ] <')
        
        # Copy C0->C1
        emit('>>[-]<< [>>+>+<<<-] >>>[-<<<+>>>] <<')
        
        # Check S (32). Flag C2=1.
        emit('>>[-]+<<') 
        emit('>' + '-'*32)
        emit('[') # Not S
            emit('[-] > [-] <') # Clear C1, Clear C2
            
            # Check F (227). Flag C3=1.
            # Recopy C0->C1
            emit('< [>+>+<<-] >> [-<<+>>] <')
            emit('>> [-]+ <<') # C3=1
            emit('-'*227)
            emit('[') # Not F
                emit('[-] >> [-] <<') # Clear C1, Clear C3
            emit(']')
        emit(']')
        
        # If C2 or C3 is set, Clear C0 to Exit Loop.
        emit('>>') # At C2
        emit('[ << [-] >> - + ]') # If C2, Clear C0. Restore C2 (Move to Temp? No, just keep 1).
        # Trick: `[ - <<[-]>> + ]` clears C0, keeps C2=1.
        
        emit('>') # At C3
        emit('[ <<< [-] >>> - + ]') # If C3, Clear C0. Keep C3=1.
        
        emit('<<<') # Back to C0
        emit(']') # End Not 0
        emit(']') # End Search Loop
        
        # --- ACTION ---
        # C2=1 if S. C3=1 if F.
        
        # If F (C3)
        emit('>>>') # To C3
        emit('[') 
        emit('[-] <<<< ,,') # Clear C3, Consume 80 80 at C0
        emit('>>>>>' + '+'*weight + '<<<<<') # Add to C5
        emit('>>>') # Back to C3
        emit(']')
        
        # If S (C2)
        emit('<') # To C2
        emit('[-]') # Clear C2
        
        emit('<<') # Back to C0
        
        
    # --- MAIN ---
    
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C4
    emit('<<<<')  # To C0
    
    read_valid_bit_fixed(4)
    emit('>>>>> [ <<<<<') 
    read_valid_bit_fixed(2)
    emit('>>>>> [ <<<<<') 
    read_valid_bit_fixed(1)
    emit('>>>>> [ <<<<<') 
    
    emit('>>>>') # To C4 (Wait, Acc is C5?)
    # Helper uses C5 for Acc.
    # `emit('>>>>>' + '+'*weight + '<<<<<')`
    # So Acc is C5.
    
    emit('>') # To C5
    
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
    
    emit('>') # To C6
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
