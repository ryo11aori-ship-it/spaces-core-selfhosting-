import sys

# Stage 9: Linear Native Compiler Generator
# Generates a Spaces program that:
# 1. Emits ELF Header.
# 2. Reads Spaces/BF source from stdin.
# 3. Translates commands (+ - > < . ,) into x64 Machine Code on the fly.
# 4. Ignores Loops ([ ]) for now (Linear only).
# 5. Emits Footer (Exit syscall).

def main():
    bf = []
    def emit(s): bf.append(s)

    # --- ELF Header (x86-64 Linux) ---
    # Entry: 0x400078
    # We use a simplified header similar to Stage 8.
    
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0, 
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00, 
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # Entry
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00, 
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        # PHeader
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, # RWX
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # FileSize (16KB buffer)
        0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, # MemSize (8MB)
        0x00, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 
    ]
    
    # Emit Header
    for b in header:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # --- Runtime Initialization ---
    # We need a pointer for the tape. Let's use r13 (callee-saved, safe).
    # mov r13, 0x600000 (Memory area)
    # Op: 49 bd 00 00 60 00 00 00 00 00
    init_code = [0x49, 0xbd, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # --- Main Compilation Loop ---
    # Read char from stdin
    emit(',[') 
    
    # We need to preserve the input char for multiple checks.
    # Structure: [Check +] > [Check -] > ...
    # Since we can't non-destructively read easily without temp vars, 
    # we will use a subtraction chain pattern.
    # Order: > < + - . , (Ignore [ ])
    
    # Char is at Cell 0. Temp at Cell 1.
    
    # 1. Check > (62)
    # 62 - 46 (.) = 16
    # 46 - 45 (-) = 1
    # 45 - 44 (,) = 1
    # 44 - 43 (+) = 1
    # 43 - 60 (<) = -17 ... wait, order matters.
    # Let's check from high to low ASCII to make subtraction easy.
    # > (62), < (60), . (46), - (45), , (44), + (43)
    
    # Check > (62)
    emit('-'*60); emit('-'*2) # Subtract 62
    emit('[>+<-]') # Move remainder to Cell 1
    emit('> [ <+>- ] <') # If Cell 1 is not 0, move back to Cell 0.
    # If Cell 0 is 0, it was MATCH >
    # This logic is tricky in raw BF generator.
    
    # SIMPLIFIED STRATEGY:
    # Just check exact matches using a copy.
    # Input C0. Copy to C1. Subtract X from C1. If C1=0, Emit Code.
    
    # Helper: Check char C. If match, output bytes BS.
    # Assumes current cell is Input Char (preserved).
    def check_emit(char_val, bytes_to_emit):
        # Copy C0 to C1 using C2 as temp
        emit('>[-]') # Clear C1
        emit('>[-]') # Clear C2
        emit('<<[>+>+<<-]>>[<<+>>-]<<') # Copy C0 -> C1, restore C0
        
        # Subtract char_val from C1
        emit('>' + '-'*char_val)
        
        # If C1 is 0, then match.
        # Use C2 as flag. Set C2=1. If C1!=0, Set C2=0.
        emit('>[-]+<') # C2 = 1
        emit('[>[-]<[-]]') # If C1!=0, Clear C2 and C1.
        
        # Now C2 is 1 if match, 0 if no match.
        emit('>') # Go to C2
        emit('[') # If match
        for b in bytes_to_emit:
            emit('[-]' + '+'*b + '.' + '[-]') # Emit byte cleanly
            # Note: We must restore C2 to 0 to exit loop? 
            # No, '[-]' at start of emit clears the temp loop var, but we need to clear C2 (current) to exit.
            # But we are using C2 as the loop counter '1'.
            # We just need to zero it at the end.
        emit('[-]]') # Zero C2 and exit
        emit('<<') # Back to C0

    # > (62): inc r13 (49 ff c5)
    check_emit(62, [0x49, 0xff, 0xc5])
    
    # < (60): dec r13 (49 ff cd)
    check_emit(60, [0x49, 0xff, 0xcd])
    
    # + (43): inc byte [r13] (41 fe 05 00) -> using offset 0
    check_emit(43, [0x41, 0xfe, 0x05, 0x00])
    
    # - (45): dec byte [r13] (41 fe 0d 00)
    check_emit(45, [0x41, 0xfe, 0x0d, 0x00])
    
    # . (46): syscall write (1, r13, 1)
    # mov rax, 1; mov rdi, 1; mov rsi, r13; mov rdx, 1; syscall
    # b8 01 00 00 00 | bf 01 00 00 00 | 4c 89 ee | ba 01 00 00 00 | 0f 05
    check_emit(46, [
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x4c, 0x89, 0xee,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ])
    
    # Loop back for next char
    emit(',]') 

    # --- Epilogue ---
    # Exit(0)
    # mov rax, 60; xor rdi, rdi; syscall
    exit_code = [0xb8, 0x3c, 0x00, 0x00, 0x00, 0x48, 0x31, 0xff, 0x0f, 0x05]
    for b in exit_code:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # Convert to Spaces
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    
    output_str = "".join([mapping.get(c, '') for c in full_bf])
    sys.stdout.buffer.write(output_str.encode('utf-8'))

if __name__ == "__main__":
    main()
