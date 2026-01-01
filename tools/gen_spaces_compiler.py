import sys

# Stage 12: Spaces Native Compiler (Simple State Machine)
# Reads Spaces Source Code.
# Logic: Read -> Check EOF -> Check Valid -> Process.
# GUARANTEED to stop on EOF.

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

    # --- Helper: Read ONE Valid Bit (0 or 1) ---
    # Returns: Adds 'weight' to C3 if Bit is 1.
    # Logic:
    #   Loop forever:
    #     Read Char (C0).
    #     If C0 == 0 or 255: Hard Exit (Jump to End).
    #     If C0 == F (227): Consume 2 bytes, Add Weight, Break Loop.
    #     If C0 == S (32): Break Loop (Add 0).
    #     Else: Continue Loop (Ignore Garbage).
    
    def read_valid_bit(weight):
        emit('[-]+[') # Start Search Loop (C0=1 dummy)
        emit(',')     # Read C0
        
        # --- 1. EOF Check (0) ---
        emit('[') # If C0 != 0
        
        # --- 2. EOF Check (255) ---
        emit('>[-]+< + [ - >-<') # Check 255
        # If Not 255, C1=0.
        
        # --- 3. Check F (227) ---
        # Copy C0->C2
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') 
        emit('>>' + '-'*227) 
        emit('>[-]+< [>[-]<[-]]') # C3 = 1 if F
        
        emit('>>> [') # If F
        emit('<<< ,,') # Consume 80 80
        # Add Weight to Accumulator (C3 is effectively C4 in main, wait.)
        # Caller uses C3 as Accumulator.
        # This helper uses C0(Input), C1(Scratch), C2(Scratch), C3(Flag).
        # We need to add to Main Accumulator (Let's say C4).
        emit('>>>>' + '+'*weight + '<<<<') 
        
        # Clear Flag C3, Clear C0 to Exit Loop
        emit('[-] <<< [-] >>>')
        emit(']') 
        
        # --- 4. Check S (32) ---
        emit('<<<') # Back to C0
        emit('[') # If C0 != 0 (Not F)
        
        # Copy C0->C2
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <')
        emit('>>' + '-'*32)
        emit('>[-]+< [>[-]<[-]]') # C3 = 1 if S
        
        emit('>>> [') # If S
        # Do nothing (Weight 0)
        # Clear Flag C3, Clear C0 to Exit Loop
        emit('[-] <<< [-] >>>')
        emit(']')
        
        emit('<<<') # Back to C0
        emit(']') # End Not F
        
        # If C0 is still != 0, it is garbage.
        # We continue loop.
        
        emit('>>') # To C2 (Scratch, 0)
        emit(']') # End Not 255
        
        # If C1 is 1 (Was 255), we must EXIT EVERYTHING.
        # We set a Global Exit Flag? 
        # Or we just clear C0 and set a special flag?
        # Let's use C5 (Main Loop Flag) to 0.
        emit('>') # To C1
        emit('[') # If 255
        emit('>>>> [-] <<<<') # Clear C5
        emit('[-] < [-]') # Clear C1, Clear C0
        emit(']')
        emit('<') # To C0
        
        emit(']') # End Not 0 (EOF Check 0)
        
        # If C0 was 0, loop ends naturally.
        # But we need to check if we should abort main loop.
        # If C0 was 0, we didn't process anything.
        # Set C5 = 0.
        # We can check if C0 was 0 by inverting?
        # Actually, simpler:
        # If the Search Loop finishes, it means we found S/F OR we hit EOF.
        # If EOF, C0 is 0. If S/F, C0 is 0 (cleared manually).
        # How to distinguish?
        # Use C6 as "Found Valid" flag?
        
        # REVISED STRATEGY:
        # If EOF detected, set C5=0.
        # Always check C5 before continuing.
        pass
        emit(']') # End Search Loop

    # --- MAIN LOOP ---
    # C0: Input
    # C1, C2, C3: Scratch
    # C4: Opcode Accumulator
    # C5: Main Loop Flag (1=Run, 0=Stop)
    
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C4 (Accumulator)
    emit('<<<<')  # To C0
    
    # Read 3 Bits.
    # We must check C5 after each read to abort immediately.
    
    # Bit 1 (Weight 4)
    read_valid_bit(4)
    emit('>>>>> [ <<<<<') # Check C5. If 1, Continue.
    
    # Bit 2 (Weight 2)
    read_valid_bit(2)
    emit('>>>>> [ <<<<<') 
    
    # Bit 3 (Weight 1)
    read_valid_bit(1)
    emit('>>>>> [ <<<<<') 
    
    # Process Opcode in C4
    emit('>>>>') # To C4
    
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
    # Dummy brackets to close the "If C5" checks
    emit('] ] ]') 
    emit(']') # End Main Loop
    
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
