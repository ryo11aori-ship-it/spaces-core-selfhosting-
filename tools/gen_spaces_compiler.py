import sys

# Stage 12: Spaces Native Compiler (EOF Fix + Indentation Check)
# Reads Spaces Source Code.
# Fixes infinite loop on EOF by explicitly checking for 0.

def main():
    bf = []
    def emit(s): bf.append(s)
    
    # --- ELF Header (64KB Safe) ---
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

    # --- Helper: Read Bits 2 and 3 (Robust) ---
    def read_bit_robust(weight):
        emit('[-]+[') # Start Loop C0=1
        emit(',') # Read
        
        # Check F (227)
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') 
        emit('>' + '-'*227) 
        emit('>[-]+< [>[-]<[-]]') 
        emit('>[ ,, >' + '+'*weight + '< <<[-]>> [-] ]') 
        
        # Check S (32)
        emit('<< [') 
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') 
        emit('>' + '-'*32)
        emit('>[-]+< [>[-]<[-]]') 
        emit('>[ <<[-]>> [-] ]') 
        emit('<< ]') 
        emit(']') 

    # --- Decoder Logic ---
    # C0: Input, C1: EOF Check, C3: Opcode, C5: Loop Flag
    
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Outer Loop
    emit('<< [-]') # Clear C3
    emit('<<<')    # To C0
    
    emit(',') # Read First Char of Triplet
    
    # EOF Check Logic:
    emit('>') # To C1
    emit('[-]+') # C1 = 1 (Assume EOF)
    emit('<') # To C0
    
    emit('[') # If C0 != 0 (Not EOF)
        emit('>-<') # C1 = 0 (Not EOF)
        
        # --- Inline Robust Logic for Bit 1 (Weight 4) ---
        # We already have C0. Loop until S/F found.
        emit('[') 
        # Check F
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') 
        emit('>' + '-'*227) 
        emit('>[-]+< [>[-]<[-]]') 
        emit('>[ ,, >++++< <<[-]>> [-] ]') 
        
        # Check S
        emit('<< [') 
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') 
        emit('>' + '-'*32)
        emit('>[-]+< [>[-]<[-]]') 
        emit('>[ <<[-]>> [-] ]') 
        
        # If Garbage, read next
        emit('<< ,') 
        emit(']') # End Check S
        emit('<<') # Back to C0
        emit(']') # End Robust Loop Bit 1
        
        # --- Read Bits 2 & 3 ---
        read_bit_robust(2)
        read_bit_robust(1)
        
        # --- Emit Opcode ---
        emit('>>>') # To C3
        
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
        
        emit('<<<') # Back to C0
        emit('[-]') # Clear C0 to exit IF
    emit(']')
    
    # Handle EOF Flag
    emit('>') # To C1
    emit('[') # If C1 is 1 (EOF was True)
        emit('>>>>') # To C5
        emit('[-]')  # C5 = 0 (Stop Loop)
        emit('<<<<') # To C1
        emit('[-]')  # Clear C1
    emit(']')
    
    emit('>>>>') # To C5
    emit(']')

    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
