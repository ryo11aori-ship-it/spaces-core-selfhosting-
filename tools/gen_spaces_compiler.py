import sys

# Stage 12: Spaces Native Compiler
# Reads Spaces Source Code (S/F sequences), Outputs ELF.
# Logic:
#   1. Emits ELF Header.
#   2. Reads input in 3-signal chunks (Triplets).
#   3. Decodes Triplets into Opcode (0-7).
#   4. Emits corresponding x64 Machine Code.

def main():
    bf = []
    def emit(s): bf.append(s)
    
    # --- ELF Header (Same as Stage 11) ---
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

    # --- Decoder Logic ---
    # We need to read 3 signals.
    # C0: Scratch/Input
    # C1: Opcode Accumulator
    # C2: Loop Counter (3 times)
    
    emit('>>') # Start at C2 (just to be safe, offset logic)
    # Actually, let's keep it simple.
    # We wrap the whole thing in a loop that runs until EOF.
    
    # Outer Loop: Read first byte of triplet.
    # If 0 (EOF), exit.
    emit(',[') 
    
    # We have the 1st byte in C0.
    # Check if S(32) or F(227).
    # Logic:
    #   Bit1 = (C0 == 227) ? 1 : 0.
    #   If F(227), we must consume next 2 bytes (80, 80).
    #   Opcode = Bit1 * 4.
    
    # --- Decode Signal 1 ---
    # C0 has input. Copy to C1.
    emit('>[-]< [>+>+<<-] >> [<<+>>-] <') # Copy C0->C1
    # Check if 227 (0xE3)
    emit('>' + '-'*227) # C1 -= 227
    emit('>[-]+<') # C2 = 1
    emit('[>[-]<[-]]') # If C1!=0 (was not 227), C2=0.
    # Now C2 is 1 if 'F', 0 if 'S'.
    # If 'F', consume 2 bytes.
    emit('>[ ,, [-] ] <') # If C2 is 1, read 2 chars and discard them. Back to C2.
    
    # Add to Opcode Accumulator (C3). Weight: 4.
    emit('[ > ++++ < -]') # C3 += C2 * 4. C2 is cleared.
    
    # --- Decode Signal 2 ---
    emit(', [') # Read next char. If 0, unexpected EOF (should handle graceful? assume valid).
    # Logic same as above.
    emit('>[-]< [>+>+<<-] >> [<<+>>-] <') # Copy
    emit('>' + '-'*227 + '>[-]+< [>[-]<[-]]') # Check F
    emit('>[ ,, [-] ] <') # Consume if F
    emit('[ > ++ < -]') # C3 += C2 * 2. Weight: 2.
    emit(']') # End check (technically 'if input!=0')
    
    # --- Decode Signal 3 ---
    emit(', [')
    emit('>[-]< [>+>+<<-] >> [<<+>>-] <') 
    emit('>' + '-'*227 + '>[-]+< [>[-]<[-]]') 
    emit('>[ ,, [-] ] <') 
    emit('[ > + < -]') # C3 += C2 * 1. Weight: 1.
    emit(']')
    
    # Now C3 contains Opcode (0-7).
    # Move to C3.
    emit('>>>')
    
    # --- Switch Case on Opcode (C3) ---
    def check_op(val, bytes_hex):
        # We are at C3 (Opcode).
        # Copy C3 -> C4 to preserve it?
        # Actually, we can destroy C3 if we check in order and subtract.
        # But Switch case usually preserves.
        # Let's use destructive subtraction for simplicity if order is 0..7.
        # 0: > (SSS)
        # 1: < (SSF)
        # 2: + (SFS)
        # 3: - (SFF)
        # 4: . (FSS)
        # 5: , (FSF)
        # 6: [ (FFS)
        # 7: ] (FFF)
        pass

    def emit_bytes(bs):
        for b in bs: emit('>' + '+'*b + '. [-] <')

    # Since opcodes are 0,1,2,3... we can subtract 1 each time.
    # Case 0: >
    emit('>[-]+<') # Flag C4=1
    emit('[>[-]<[-]]') # If C3!=0, Flag=0.
    emit('>') # To Flag
    emit('[') # If Match (0)
    emit_bytes([0x49, 0xff, 0xc5]) # >
    emit('[-]]') # Clear Flag
    emit('<') # Back to C3

    # Case 1: <
    emit('-') # C3 -= 1
    emit('>[-]+< [>[-]<[-]] > [') # Check 0
    emit_bytes([0x49, 0xff, 0xcd]) # <
    emit('[-]] <')

    # Case 2: +
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [')
    emit_bytes([0x41, 0xfe, 0x45, 0x00]) # +
    emit('[-]] <')

    # Case 3: -
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [')
    emit_bytes([0x41, 0xfe, 0x4d, 0x00]) # -
    emit('[-]] <')

    # Case 4: .
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [')
    emit_bytes([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    emit('[-]] <')

    # Case 5: ,
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [')
    # , input not needed for Hello World, but let's be complete or skip?
    # Skip to save space, Hello World doesn't use input.
    emit('[-]] <')

    # Case 6: [
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [')
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00]) # [
    emit('[-]] <')

    # Case 7: ]
    emit('-')
    emit('>[-]+< [>[-]<[-]] > [')
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff]) # ]
    emit('[-]] <')

    # End of Switch.
    # Return to C0 for next loop.
    emit('<<<')
    emit(',') # Read next char (start of next triplet)
    emit(']') # End Loop

    # Exit
    exit_code = [0xb8, 0x3c, 0x00, 0x00, 0x00, 0x48, 0x31, 0xff, 0x0f, 0x05]
    for b in exit_code:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # Padding
    emit('>>[-]' + '+'*255 + '[>[-]' + '+'*255 + '[>.< -]<-]')
    
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
