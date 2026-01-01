import sys

# Stage 12: Spaces Native Compiler (Final Fix)
# Reads Spaces Source Code.
# Logic: Simple State Machine (Read -> Check EOF -> Check Valid -> Loop/Exit).
# Features: Padding Restored, Infinite Loop Fixed.

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
    # Scans input until S or F is found. Ignores Garbage.
    # Handles EOF (0 or 255) by clearing C0.
    def read_valid_bit(weight):
        emit('[-]+[') # Start Loop (Assume C0=1 to enter)
        emit(',')     # Read C0
        
        # Check EOF (0)
        emit('[')     # If C0!=0
        
        # Check EOF (255)
        emit('>[-]+< + [ - >-<') # C1=0 if Not 255
        
        # Check F (227)
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') 
        emit('>>' + '-'*227) 
        emit('>[-]+< [>[-]<[-]]') # C3=1 if F
        
        emit('>>> [') # If F
        emit('<<< ,,') # Consume 80 80
        emit('>>>>' + '+'*weight + '<<<<') # Add Weight
        emit('[-] <<< [-] >>>') # Clear C3, Clear C0 -> Exit Loop
        emit(']') 
        
        # Check S (32)
        emit('<<<') # Back to C0
        emit('[') # If C0!=0 (Not F)
        
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') 
        emit('>>' + '-'*32) 
        emit('>[-]+< [>[-]<[-]]') # C3=1 if S
        
        emit('>>> [') # If S
        # Weight 0
        emit('[-] <<< [-] >>>') # Clear C3, Clear C0 -> Exit Loop
        emit(']')
        
        emit('<<<') # Back to C0
        emit(']') # End Not F
        
        emit('>>') # To C2 (Scratch)
        emit(']') # End Not 255
        
        # If C1=1 (Was 255/EOF), Clear C0 to ensure Exit
        emit('>') # To C1
        emit('[ >>>>[-]<<<< [-]<[-] ]') # Clear C5(MainFlag), C1, C0
        emit('<') # To C0
        
        emit(']') # End Not 0 (EOF)
        # If C0 was 0 (EOF), Loop exits.
        
        # If C0 was Garbage (Not 0, 255, S, F):
        # The checks didn't clear C0.
        # Loop repeats -> Reads next char.
        emit(']') # End Search Loop

    # --- MAIN LOOP ---
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C4 (Accumulator)
    emit('<<<<')  # To C0
    
    # Read 3 Bits
    read_valid_bit(4)
    emit('>>>>> [ <<<<<') # Check C5
    read_valid_bit(2)
    emit('>>>>> [ <<<<<') 
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
    emit('] ] ]') 
    emit(']') # End Main Loop
    
    # --- PADDING (Restored!) ---
    # Emit 64KB zeros to satisfy ELF header
    emit('>>[-]' + '+'*255 + '[>[-]' + '+'*255 + '[>.< -]<-]')

    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
