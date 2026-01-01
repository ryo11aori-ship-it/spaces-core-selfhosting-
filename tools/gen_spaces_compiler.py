import sys

# Stage 12: Spaces Native Compiler (Overflow Fix)
# Reads Spaces Source Code (S/F sequences), Outputs ELF.
# Fixes infinite loop on garbage characters.

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
    def read_bit_robust(weight):
        # We start at C0.
        emit('[-]') # Ensure C0 starts clean
        
        # Start Loop: runs until we successfully process S or F
        emit('+[')  
        
        # Read a char into C0
        emit(',')
        
        # Check EOF (0). If 0, we are stuck.
        # But for robust reading, if 0, we should probably stop?
        # The outer loop handles EOF, but here we are mid-triplet.
        # Let's assume if 0, it behaves like S (0) or just exits.
        # Simplified: If 0, treat as S (do nothing, exit loop).
        
        # Check F (227)
        emit('>[-]< [>+>+<<-] >> [<<+>>-] <') # Copy C0->C1
        emit('>' + '-'*227) 
        emit('>[-]+< [>[-]<[-]]') # C2 = 1 if F
        
        emit('>[') # If F (C2==1)
            emit(',,') # Consume 80 80
            emit('>' + '+'*weight + '<') # Add to C3
            emit('<< [-] >>') # Clear C0 to Exit Loop
            emit('[-]') # Clear C2
        emit(']') # End If F
        
        # Check S (32)
        emit('<<') # Back to C0
        emit('[') # If C0 != 0 (Not F)
            emit('>[-]< [>+>+<<-] >> [<<+>>-] <') # Copy C0->C1
            emit('>' + '-'*32)
            emit('>[-]+< [>[-]<[-]]') # C2 = 1 if S
            
            emit('>[') # If S
                # Add 0 (Nothing)
                emit('<< [-] >>') # Clear C0 to Exit Loop
                emit('[-]')
            emit(']') # End If S
            
            # If C0 is still != 0, it means Garbage (Newline, etc).
            # We are at C2 (which is 0).
            emit('<<') # Back to C0.
            # We do NOT clear C0 here, because the loop condition relies on it.
            # But we MUST read a new char to progress.
            # Wait, the loop start is `emit(',')`.
            # So if we just loop back, we will read again!
            # BUT: The loop is `+[ ... ]`.
            # We need to make sure C0 is non-zero to repeat.
            # If C0 was garbage (e.g. 10), it is non-zero.
            # So we just hit `]` and loop back.
            # AND the first thing in loop is `,` which overwrites C0.
            # THIS IS CORRECT!
            
            # ... Wait, previous crash was "Tape pointer overflow".
            # If we just loop back, we are fine.
            # Why did it crash?
            # Maybe the loop condition `+[` assumes we enter once.
            # Inside: `[-],`. This clears the flag `1` and reads input.
            # If input is 10 (Newline).
            # Check F -> Fail. C0 is 10.
            # Check S -> Fail. C0 is 10.
            # Loop `]` checks C0. 10 != 0. Repeats.
            # Inside: `[-],`. Clears 10. Reads next char.
            
            # Logic seems sound. Why crash?
            # "Tape pointer overflow (Right)".
            # Maybe I am moving Right somewhere unbounded?
            
            # Ah! `read_bit_robust` uses C0, C1, C2, C3.
            # It expects to start at C0.
            # Is it possible we are drifting?
            # The calls are `read_bit_robust(4)`, `read_bit_robust(2)`...
            # Between calls, do we return to C0?
            
            # Let's check `main`.
            # `emit('>>') # Start at C2`
            # `emit(', [') # Check EOF`
            # `emit('>>>[-]+') # C5 = 1`
            # `emit('[')` (Outer loop)
            # `emit('<<[-]')` -> Moves from C5 to C3. Clears C3.
            
            # Wait. `read_bit_robust` assumes we are at C0?
            # "We start at C0." comment says so.
            # But `read_bit_robust` starts with `emit('[-]')`.
            # If we are at C3, and we call it...
            # `read_bit_robust` does `emit('[-]')`. Clears C3.
            # Then uses C3 as "C0".
            # Uses C4 as "C1", C5 as "C2", C6 as "C3" (Accumulator).
            # But the caller expects Accumulator at C3!
            
            # POINTER MISMATCH!
            # The caller `main` is at C3 when it calls `read_bit_robust`.
            # But `read_bit_robust` logic is written relative to "C0".
            # If it runs relative to C3:
            # It puts result in "C3" (relative) -> C6 (absolute).
            # But `main` expects result in C3 (absolute).
            
            # FIX:
            # Before calling `read_bit_robust`, we must move to C0.
            # `emit('<<<')` (From C3 to C0).
            pass
            
    # --- Decoder Logic ---
    # Global Layout:
    # C0: Input Buffer / Scratch
    # C1: Scratch
    # C2: Scratch
    # C3: Opcode Accumulator
    # C4: Unused
    # C5: Loop Flag
    
    emit('>>>>>') # Start at C5
    emit('[-]+')  # C5 = 1
    emit('[')     # Outer Loop
        # Go to C3 and clear it
        emit('<< [-]') 
        
        # Go to C0 to run reader
        emit('<<<')
        
        # Read 3 bits. Result adds to C3.
        # Since read_bit_robust ends at C0, we are fine chaining them.
        read_bit_robust(4)
        read_bit_robust(2)
        read_bit_robust(1)
        
        # Now result is in C3. We are at C0.
        # Go to C3.
        emit('>>>')
        
        # --- Switch Case ---
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
        
        # Return to C5
        emit('>>') 
    emit(']')

    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
