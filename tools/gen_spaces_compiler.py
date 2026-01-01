import sys

# Stage 12: Spaces Native Compiler (Robust Version - Fixed Indentation)
# Reads Spaces Source Code (S/F sequences), Outputs ELF.
# Ignores Newlines (10) and other garbage chars.

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

    # --- Helper: Read 1 Bit (Robust) ---
    # Adds 'weight' to C3 if the bit is 1 (F).
    # Loops until it finds 'S' (32) or 'F' (227).
    def read_bit_robust(weight):
        emit('[-]') # Clear C0
        emit('+[')  # Start Loop (Wait for valid char)
        emit('[-],') # Read C0
        
        # Check F (227)
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') # Copy C0->C1
        emit('>' + '-'*227) 
        emit('>[-]+< [>[-]<[-]]') # C2 = 1 if F
        
        emit('>[') # If F
        emit(',,') # Consume 80 80
        # Add weight to C3
        emit('>' + '+'*weight + '<')
        # Set C0 = 0 to Exit Loop
        emit('<< [-] >>') 
        # Clear C2
        emit('[-]')
        emit(']') # End If F
        
        # Check S (32)
        # Restore C0 check. We are at C2 (0).
        emit('<<') # Back to C0.
        
        # If C0 is 0 (Matched F), we are done.
        # If C0 is not 0, Check S.
        emit('[') # If C0 != 0
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') # Copy C0->C1
        emit('>' + '-'*32)
        emit('>[-]+< [>[-]<[-]]') # C2 = 1 if S
        
        emit('>[') # If S
        # Add 0 to C3 (Do nothing)
        # Set C0 = 0 to Exit Loop
        emit('<< [-] >>')
        emit('[-]')
        emit(']') # End If S
        
        # If C0 is still not 0 (Neither F nor S), continue loop
        emit('<<') # Back to C0
        emit(']') # End Loop

    # --- Decoder Logic ---
    emit('>>') # Start at C2
    emit(', [') # Check EOF (Trigger only on input present)
    
    emit('>>>[-]+') # C5 = 1 (Loop Flag)
    emit('[') 
    # C3 (Accumulator) = 0
    emit('<<[-]')
    
    # Read 3 bits
    read_bit_robust(4)
    read_bit_robust(2)
    read_bit_robust(1)
    
    # Now C3 has Opcode.
    def emit_bytes(bs):
        for b in bs: emit('>' + '+'*b + '. [-] <')

    # Move to C3
    emit('<<<') 
    
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

    # Case 5: , (Skip)
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
    
    emit('>>') # Back to C5
    emit(']')

    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
