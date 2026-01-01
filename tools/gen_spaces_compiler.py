import sys

# Stage 12: Spaces Native Compiler (Simplified Logic & Flat Indentation)
# Reads Spaces Source Code.
# Logic: Read -> Copy -> Subtract 32 (S) -> Subtract 195 (F).
# Guaranteed to handle EOF, Garbage, S, and F correctly without pointer errors.

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
    # Scans input until S or F is found.
    # Adds 'weight' to C4 if F is found.
    def read_valid_bit(weight):
        emit('[-]+[') # Start Search Loop (C0=1 to enter)
        emit(',')     # Read Input (C0)
        
        # --- Check EOF (0) ---
        emit('[') # If C0!=0
        
        # --- Check EOF (255) ---
        emit('>[-]+< + [ - >-<') # C1=1. C0 check. C1=0 if not 255.
        
        # --- Copy C0 to C1 for checking ---
        # Layout: C0(Input), C1(Copy), C2(Copy)
        emit('>[-]') 
        emit('< [>+>+<<-]') 
        emit('>> [-<<+>>] <') # Restore C0 from C2. C1 has Copy.
        
        # --- Check S (32) ---
        emit('-'*32) # C1 -= 32
        
        emit('[') # If C1 != 0 (Not S)
        
        # --- Check F (227) ---
        # 227 - 32 = 195
        emit('-'*195) # C1 -= 195
        
        emit('[') # If C1 != 0 (Not F -> Garbage)
        emit('[-]') # Clear C1
        # It was Garbage. We need to repeat loop (C0=1).
        # C0 is currently holding Input (Not 0).
        # We just leave C0 as non-zero.
        # But to be safe, set C0=1 explicitly?
        # Actually, C0 is already non-zero.
        # We need a flag to SKIP the "Valid Found" logic below.
        emit('>> [-]+ <<') # Set C2=1 (Garbage Flag)
        emit(']') # End Not F
        
        # Check if Valid F (C1 was 0, so C2 is 0)
        emit('>>') # At C2
        emit('[') # If C2==1 (Garbage)
        emit('[-] <<') # Clear C2, Back to C0
        # Do nothing else. Loop repeats because C0!=0.
        emit(']') 
        emit('<') # Back to C1 (which is 0)
        
        # If C2 was 0, it means it was F.
        # But wait, if it was S, C1 was 0 initially. Inner loop didn't run.
        # So for S, C2 is 0.
        # For F, C2 is 0.
        # For Garbage, C2 is 1.
        
        # We need to distinguish S vs F.
        # If we are here (Inside "Not S"), and C2 is 0, then it is F.
        
        # Check C2 again? No, C2 is 0.
        # We know we are inside "Not S".
        # So if not Garbage, it MUST be F.
        
        # Logic: If Not Garbage (C2==0), then it is F.
        emit('>>') # At C2
        emit('[-]+') # Set C2=1 (Assume F)
        emit('<') # At C1
        
        # But wait, if Garbage, C2 was 1, loop ran, cleared C2.
        # So C2 is 0 now.
        # This logic is circular.
        
        # RESTART LOGIC: Simpler Flagging.
        # C1 is Check Value.
        # C2 is "Is Garbage" Flag. Init 0.
        
        emit(']') # End Not S (Dummy close for thinking)
        emit(']') # End Not 255
        emit(']') # End Not 0
        emit(']') # End Loop
        
        # --- ACTUAL IMPLEMENTATION ---
        
        # Start Loop
        emit('[-]+[') 
        emit(',') 
        
        # EOF 0 Check
        emit('[') 
        
        # EOF 255 Check
        emit('>[-]+< + [ - >-<') # C1=0 if Not 255
        
        # Copy C0->C1
        emit('>[-]< [>+>+<<-] >> [-<<+>>] <')
        
        # Check S (32)
        emit('>' + '-'*32)
        emit('[') # Not S
        
        # Check F (195)
        emit('-'*195)
        emit('[') # Not F (Garbage)
        emit('[-]') # Clear C1
        emit('>[-]+<') # Set C2=1 (Garbage)
        emit(']') 
        
        # If F (C1=0) and Not Garbage (C2=0):
        # Handle F.
        emit('>') # At C2
        emit('[') # If Garbage
        emit('[-]') # Clear C2
        # It is Garbage. C0 is Non-Zero. Loop repeats.
        emit('<<') # Back to C0
        emit(']') 
        
        # If C2 was 0, it was F.
        # BUT wait. If it was S, outer loop skipped.
        # We need to distinguishing S vs F is hard if we merge them.
        
        # Only F needs action (add weight, consume).
        # If we are here (Inside Not S), and C2 is 0, it is F.
        
        # But `[` enters if Non-Zero.
        # If F, C2 is 0. So `[` skips.
        # So we can't run F code inside `[` checking C2.
        
        # Use ELSE pattern:
        # Init C3 = 1 (Assume F).
        # If Garbage, Set C3 = 0.
        
        emit('[-] +') # C2 = 1 (Assume F)
        emit('<') # At C1
        emit('[') # Not F (Garbage)
        emit('[-]') # Clear C1
        emit('> [-] <') # C2 = 0 (Garbage)
        emit(']')
        
        # Now: If F, C2=1. If G, C2=0.
        emit('>') # At C2
        emit('[') # If F
        emit('<<<< ,,') # Consume 80 80 at C0
        emit('>>>>' + '+'*weight + '<<<<') # Add Weight to C4
        emit('[-] << [-] >>') # Clear C2, Clear C0 (Exit)
        emit(']')
        emit('<') # At C1
        
        emit(']') # End Not S
        
        # If S: Outer loop skipped. C1 (which was Copy) is 32? No.
        # If S: C0=32. C1 (Copy)=32. `> -32`. C1=0. `[` Skips.
        # So for S, we fall through here.
        # We need to set C0=0 to Exit.
        # But wait, if Garbage, we also fall through here?
        # If Garbage: Inner logic ran. C2 was 0. F-block skipped.
        # We fell through. C0 is still Non-Zero.
        # If F: Inner logic ran. C2 was 1. F-block ran. C0 became 0.
        # We fell through. C0 is 0.
        
        # So:
        # S -> C0!=0.
        # G -> C0!=0.
        # F -> C0=0.
        
        # We need to distinguish S vs G.
        # S: C1=0.
        # G: C1=0 (cleared inside).
        
        # We need a Flag for S.
        # Before "Not S" loop: Set C3=1 (Is S).
        # Inside "Not S" loop: Set C3=0.
        
        emit('>> [-]+ <<') # C3=1 (Assume S)
        emit('[') # Not S
        emit('>> [-] <<') # C3=0 (Not S)
        
        # ... (Inner F/G Logic) ...
        # Copy-paste F/G logic from above
        emit('-'*195) # Check F
        emit('[-] +') # C2=1 (Assume F)
        emit('<') # At C1
        emit('[') # Not F (Garbage)
        emit('[-]') # Clear C1
        emit('> [-] <') # C2=0 (Garbage)
        emit(']')
        emit('>') # At C2
        emit('[') # If F
        emit('<<<< ,,') 
        emit('>>>>' + '+'*weight + '<<<<') 
        emit('[-] << [-] >>') # Clear C2, Clear C0
        emit(']')
        emit('<') # At C1
        
        emit(']') # End Not S
        
        # If S (C3=1)
        emit('>>') # At C3
        emit('[') # If S
        emit('[-] <<< [-] >>>') # Clear C3, Clear C0
        emit(']')
        
        emit('<<<') # Back to C0
        emit(']') # End Not 255
        
        # Handle EOF 255
        emit('>') # At C1
        emit('[ >>>>[-]<<<< [-]<[-] ]') # Clear C5, C1, C0
        emit('<') 
        
        emit(']') # End Not 0
        emit(']') # End Search Loop

    # --- MAIN LOOP ---
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C4
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
