import sys

# Stage 12: Spaces Native Compiler (EOF 255 Fix)
# Reads Spaces Source Code.
# Fixes infinite loop by treating 255 (-1) as EOF.

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

    # --- Helper: Check if EOF (0 or 255) ---
    # Input: C0. Output: C0 is 0 if EOF, non-zero if NOT EOF.
    # Side effects: Uses C1 as scratch. C0 is preserved (if not EOF) or 0 (if EOF).
    # Logic: If C0==0 -> EOF. If C0==255 -> EOF.
    # Implementation:
    #   If C0==0, done.
    #   If C0!=0:
    #     Check if 255. (C0+1 == 0).
    #     If 255, Set C0=0.
    #     Else, Restore C0.
    # This helper is inlined where needed.

    # --- Helper: Read Bits 2 and 3 (Robust) ---
    def read_bit_robust(weight):
        emit('[-]+[') 
        emit(',') 
        
        # Check EOF (255) inside robust loop
        # If 255, treat as End -> Exit loop (by setting C0=0 and cleaning up)
        emit('>[-]+ <') # C1=1
        emit('+') # C0 += 1. If it was 255, now 0.
        emit('[') # If C0 != 0 (Was not 255)
        emit('-') # Restore C0
        emit('>-<') # C1=0 (Not 255)
        
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
        emit(']') # End "Not 255" block
        
        # If C1 is still 1, it meant it WAS 255 (EOF).
        # We need to ensure we exit the loop (C0 is already 0 from overflow).
        # And ensure we are at C0.
        # The loop condition checks C0.
        # If 255 -> C0 became 0. Loop ends.
        
        # Clean up C1
        emit('>[-]<')
        
        emit(']') # Loop End

    # --- Decoder Logic ---
    emit('>>>>>') # To C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Outer Loop
    emit('<< [-]') 
    emit('<<<')    
    emit(',') # Read First Char
    
    # EOF Check (0 or 255)
    emit('>[-]+ <') # C1=1
    emit('+') # Test 255
    emit('[') # Not 255
    emit('-') # Restore
    emit('>-<') # C1=0
    
    # If C0 is 0 (Real 0), loop won't run, C1 remains 0 (wait, logic error).
    # If C0 was 0: `+` -> 1. Loop runs. Restore -> 0. C1 -> 0.
    # So 0 is treated as Not EOF? No.
    # Let's check 0 separately.
    
    # Correct Logic:
    # If C0 == 0: Exit.
    # If C0 == 255: Exit.
    
    # Check 0:
    emit('[') # If C0 != 0
        # Check 255
        emit('>[-]+<') # C1=1
        emit('+') # Check overflow
        emit('[') # Not 255
            emit('-') # Restore
            emit('>-<') # C1=0 (Valid char)
            
            # --- Inline Robust Bit 1 ---
            # C0 is Valid Char. Process it.
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
            emit('<< ,') 
            
            # Check EOF (255) inside robust skipper
            emit('>[-]+< + [ - >-<') # If not 255, restore C0 and C1=0
            # If 255, C0 is 0, Loop terminates.
            emit('] >[-]<') # Clear C1
            
            emit(']') 
            emit('<<') 
            emit(']') # End Robust Bit 1
            
            # Bits 2 & 3
            read_bit_robust(2)
            read_bit_robust(1)
            
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
            
            emit('<<<') 
            
        emit(']') # End Not 255
        
        # If C1 is 1 (Was 255), we fall through here.
        # We need to Exit Main Loop.
        emit('>') # To C1
        emit('[') 
        emit('>>>>') # To C5
        emit('[-]') # Clear Flag
        emit('<<<<') # To C1
        emit('[-]') # Clear C1
        emit(']')
        emit('<') # To C0
        emit('[-]') # Clear C0 to exit wrapping loop
        
    emit(']') # End Not 0
    
    emit('>>>>') 
    emit(']')

    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
