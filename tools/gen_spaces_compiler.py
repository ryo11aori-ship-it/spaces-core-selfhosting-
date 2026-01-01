import sys

# Stage 12: Spaces Native Compiler (Clean & Robust)
# Logic: Read -> Identify(S/F) -> Set Flags -> Exit Loop -> Process.
# No extra comments or dead code to cause IndentationError.

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
    # C0: Input, C1: Copy, C2: FlagS, C3: FlagF, C4: Temp
    def read_valid_bit(weight):
        emit('[-]+[') 
        emit(',') # Read C0
        
        # Check EOF 0
        emit('[') 
        
        # Check EOF 255
        # C1=1 if 255. C0 restored if not 255.
        emit('>[-]+< + [ - >-< ]')
        
        # If 255 (C1=1), Exit All
        emit('>') # At C1
        emit('[ >>>>>[-]<<<<< [-]<[-] ]') # Clear C6(MainFlag), C1, C0
        emit('<') # At C0
        
        # Clear Flags C2, C3
        emit('>> [-] > [-] <<<')
        
        # Copy C0 -> C1 using C4 as temp
        # Layout: C0, C1, C2, C3, C4
        emit('>>>> [-] <<<<') # Clear C4
        emit('[ >+ >>>+ <<<< -] >>>> [- <<<<+>>>> ] <<<<') # C0->C1,C4 -> C0
        
        # Check S (32) on C1
        emit('>> [-]+ <<') # Assume S (C2=1)
        emit('>' + '-'*32) # C1 -= 32
        
        emit('[') # If C1!=0 (Not S)
            emit('[-] > [-] <') # Clear C1, Clear C2
            
            # Check F (227)
            # Recopy C0 -> C1
            emit('< [ >+ >>>+ <<<< -] >>>> [- <<<<+>>>> ] <<<<')
            
            emit('>>> [-]+ <<<') # Assume F (C3=1)
            emit('>' + '-'*227) # C1 -= 227
            
            emit('[') # If C1!=0 (Not F -> Garbage)
                emit('[-] >> [-] <<') # Clear C1, Clear C3
            emit(']')
        emit(']') # End Not S
        
        # If C2 or C3 is set, Clear C0 to Exit Loop
        emit('>>') # At C2
        emit('[ << [-] >> - + ]') # If C2, Clear C0, Keep C2
        emit('>') # At C3
        emit('[ <<< [-] >>> - + ]') # If C3, Clear C0, Keep C3
        
        emit('<<<') # Back to C0
        emit(']') # End Not 0 (EOF check)
        emit(']') # End Search Loop
        
        # --- Process Flags ---
        # If F (C3=1)
        emit('>>>') # At C3
        emit('[')
        emit('[-] <<<< ,,') # Clear C3, Consume 2 bytes at C0
        emit('>>>>>' + '+'*weight + '<<<<<') # Add to C5 (Acc)
        emit('>>>') # Back to C3
        emit(']')
        
        # If S (C2=1)
        emit('< [-]') # Clear C2
        
        emit('<<') # Back to C0

    # --- MAIN LOOP ---
    # C0: Input
    # C1-C4: Scratch/Flags
    # C5: Opcode Accumulator
    # C6: Main Loop Flag
    
    emit('>>>>>>') # To C6
    emit('[-]+')  # C6 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C5
    emit('<<<<<')  # To C0
    
    # Read 3 Bits
    read_valid_bit(4)
    emit('>>>>>> [ <<<<<<') # Check Main Flag C6
    read_valid_bit(2)
    emit('>>>>>> [ <<<<<<') 
    read_valid_bit(1)
    emit('>>>>>> [ <<<<<<') 
    
    # Process Opcode in C5
    emit('>>>>>') 
    
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
    emit('] ] ]') # Close checks
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
