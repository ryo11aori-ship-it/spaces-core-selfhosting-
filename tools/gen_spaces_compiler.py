import sys

# Stage 12: Spaces Native Compiler (Pointer Logic Fixed)
# Reads Spaces Source Code.
# Fixes the bug where S/F checks were looking at the wrong memory cells.

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
        emit(',')     # Read C0
        
        # --- Check EOF (0) ---
        emit('[') # If C0!=0
        
        # --- Check EOF (255) ---
        emit('>[-]+< + [ - >-<') # Check 255. Result in C1 (0=255, 1=Not 255)
        
        # --- Check F (227) ---
        # Copy C0 to C1 and C2, Restore C0 from C2. End at C1.
        emit('>[-]') # Clear C1
        emit('< [>+>+<<-]') # C0 -> C1, C2
        emit('>> [-<<+>>] <') # C2 -> C0. End at C1.
        
        emit('-'*227) # Subtract 227 from C1
        
        # Check if C1 is 0. Set C2=1 if Match.
        emit('>[-]+') # Set C2=1
        emit('< [ >[-] < [-] ]') # If C1!=0, Clear C2, Clear C1.
        
        # If Match (C2=1)
        emit('>') # To C2
        emit('[') 
        emit('<< ,,') # Consume 80 80 at C0
        emit('>>>>' + '+'*weight + '<<<<') # Add Weight to C4
        emit('[-]') # Clear C0 to Exit Loop
        emit('>> [-]') # Clear C2
        emit(']') 
        emit('<<') # Back to C0
        
        # --- Check S (32) ---
        emit('[') # If C0!=0 (Not F)
        
        # Copy C0 to C1...
        emit('>[-]< [>+>+<<-] >> [-<<+>>] <') # End at C1
        
        emit('-'*32) # Subtract 32
        
        # Check Match
        emit('>[-]+ < [ >[-] < [-] ]') # C2=1 if Match
        
        emit('>') # To C2
        emit('[')
        # Weight 0 (Do nothing)
        emit('<< [-]') # Clear C0 to Exit Loop
        emit('>> [-]') # Clear C2
        emit(']')
        emit('<<') # Back to C0
        
        emit(']') # End Not F
        
        emit('>>') # To C2
        emit(']') # End Not 255
        
        # Handle EOF 255 (C1=1)
        emit('>') # To C1
        emit('[ >>>>[-]<<<< [-]<[-] ]') # Clear C5, C1, C0
        emit('<') # To C0
        
        emit(']') # End Not 0
        emit(']') # End Search Loop

    # --- MAIN LOOP ---
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C4 (Accumulator)
    emit('<<<<')  # To C0
    
    # Read 3 Bits
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
