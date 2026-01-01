import sys

# Stage 12: Spaces Native Compiler (Pointer Logic Strictly Fixed)
# Reads Spaces Source Code.
# Fixes pointer drift in read_valid_bit.

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
        emit(',')     # Read Input to C0
        
        # --- Check EOF (0) ---
        emit('[') # If C0!=0
        
        # --- Check EOF (255) ---
        # Logic: C1 = (C0 != 255)
        emit('>[-]+<') # C1=1
        emit('+') # C0 += 1
        emit('[') # If C0!=0 (Original was not 255)
        emit('-') # Restore C0
        emit('>-<') # C1=0
        
        # --- Check F (227) ---
        # We are at C1 (which is 0). Go to C0.
        emit('<') 
        
        # Copy C0 to C2 and C3. Restore C0 from C3.
        # Temp Layout: C0(Input), C1(0), C2(Copy), C3(Copy)
        emit('>> [-] > [-] <<<') # Clear C2, C3. Back to C0.
        emit('[ >>+>+<<<- ]') # Move C0 -> C2, C3
        emit('>>> [-<<<+>>>] <') # Move C3 -> C0. We are at C2.
        
        # Compare C2 with 227
        emit('-'*227)
        # Result C2 is 0 if Match.
        
        # Set C3=1 if Match (C2==0)
        emit('>[-]+') # C3=1
        emit('< [ >[-] < [-] ]') # If C2!=0, Clear C3, Clear C2.
        
        # If Match (C3=1)
        emit('>') # To C3
        emit('[')
        # Consume 80 80 at C0 (We are at C3)
        emit('<<< ,,') 
        # Add Weight to C4
        emit('>>>>' + '+'*weight + '<<<<') 
        # Clear C3 (Self), Clear C0 to Exit Loop
        emit('[-] <<< [-] >>>')
        emit(']')
        emit('<<<') # Back to C0
        
        # --- Check S (32) ---
        emit('[') # If C0!=0 (Not F)
        
        # Copy C0 to C2, C3. Restore C0 from C3.
        emit('>> [-] > [-] <<<') 
        emit('[ >>+>+<<<- ]') 
        emit('>>> [-<<<+>>>] <') # We are at C2.
        
        # Compare C2 with 32
        emit('-'*32)
        
        # Set C3=1 if Match (C2==0)
        emit('>[-]+ < [ >[-] < [-] ]')
        
        emit('>') # To C3
        emit('[')
        # Weight 0
        # Clear C3, Clear C0 to Exit Loop
        emit('[-] <<< [-] >>>')
        emit(']')
        emit('<<<') # Back to C0
        
        emit(']') # End Not F
        
        # Back to C1 check
        emit('>') # To C1
        emit(']') # End Not 255
        
        # If C1=1 (Was 255), Clear Everything to Exit
        # We are at C1.
        emit('[ >>>>[-]<<<< [-]<[-] ]') 
        emit('<') # To C0
        
        emit(']') # End Not 0
        
        # If C0 was cleared (Found S/F or EOF), Loop Ends.
        emit(']') # End Search Loop

    # --- MAIN LOOP ---
    # Layout: C0=Input, C1-C3=Scratch, C4=Acc, C5=Flag
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Main Loop
    
    emit('< [-]') # Clear C4
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
