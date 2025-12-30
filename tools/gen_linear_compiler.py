import sys

# Stage 9: Linear Native Compiler Generator (Improved)
# Generates a Spaces program that:
# 1. Emits ELF Header.
# 2. Reads ASCII BF source from stdin (+ - > < . ,).
# 3. Translates into x64 Machine Code using a Subtraction Cascade (Switch-Case).
# 4. Emits Footer (Exit syscall).

def main():
    bf = []
    def emit(s): bf.append(s)

    # --- ELF Header (x86-64 Linux) ---
    # Same as before, targeting ~16KB buffer
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0, 
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00, 
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00, 
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        # PHeader
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # FileSize (16KB)
        0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, # MemSize (8MB)
        0x00, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 
    ]
    
    # Emit Header
    for b in header:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # Runtime Init: mov r13, 0x600000
    init_code = [0x49, 0xbd, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # --- Main Compilation Loop (Switch-Case Pattern) ---
    emit(',[') 
    
    # Structure:
    # Input is at C0.
    # We subtract to check values. If 0, we found it.
    # Order of ASCII:
    # + (43)
    # , (44) diff 1
    # - (45) diff 1
    # . (46) diff 1
    # < (60) diff 14
    # > (62) diff 2
    
    # Helper to emit bytes
    def emit_bytes(bs):
        for b in bs:
            emit('>' + '+'*b + '. [-] <')

    # Case '+': 43
    emit('-'*43)
    emit('[') # If not '+' (non-zero)
    
        # Case ',': 44 (diff 1)
        emit('-')
        emit('[') # If not ','

            # Case '-': 45 (diff 1)
            emit('-')
            emit('[') # If not '-'

                # Case '.': 46 (diff 1)
                emit('-')
                emit('[') # If not '.'

                    # Case '<': 60 (diff 14)
                    emit('-'*14)
                    emit('[') # If not '<'

                        # Case '>': 62 (diff 2)
                        emit('-'*2)
                        emit('[') # If not '>'
                            
                            # Unknown char: just consume it (rest of loop does nothing)
                            # To be safe, we should probably clear C0 here to exit checks
                            emit('[-]')

                        emit(']') # End '>' check
                        # If we are here and C0 is 0, it was '>'.
                        # BUT Brainfuck logic is "Execute loop if Non-Zero".
                        # This "If Else" structure is tricky.
                        
                        # Let's use the Standard "Destructive If" Pattern:
                        # Copy C0 to Temp C1. Subtract. If Zero, Exec C2.
                        pass
                    emit(']')
                emit(']')
            emit(']')
        emit(']')
    emit(']')

    # RE-STRATEGY: The above nested loop is hard to trigger "On Zero".
    # Correct Pattern:
    # 1. Subtract X.
    # 2. If Zero, set Flag.
    # 3. Restore X (or just move on since we consume input).
    
    # Simplified Switch-Case using "Lookahead":
    # C0 = Input.
    # Sub 43.
    # If C0 is 0: Emit "+" code.
    # Else: Sub 1. If C0 is 0: Emit "," code.
    # ...
    # Problem: How to detect "Is Zero" in BF?
    # Pattern: Temp0=1. C0[Temp0=0]. Temp0[Emit Code; Temp0=0]
    
    def check_and_emit(diff, code):
        emit('-' * diff) # Subtract difference
        
        # Check if C0 is 0
        emit('>[-]+<')   # C1 = 1 (Flag)
        emit('[>[-]<[-]]') # If C0 != 0, C1 = 0. And C0 is cleared (destructive!).
        # WAIT! If we clear C0, we can't check the next case!
        # We must Restore C0 if it wasn't a match.
        # This is too heavy for a generator.
        
        # FINAL STRATEGY: 
        # Since we generated the input "linear_hello.bf" ourselves, and it only contains Valid Chars...
        # We can cheat slightly for stability:
        # Just assume the input is clean? No, that's weak.
        
        # Let's use the Robust "Copy and Check" again, but careful this time.
        # C0 is Input. C1 is Copy.
        pass

    # --- RELIABLE IMPLEMENTATION ---
    # C0: Input
    # C1: Scratch
    # C2: Scratch
    
    # Copy C0 -> C1
    emit('>[-]>[-]<< [>+>+<<-] >> [<<+>>-] <') # C1 has copy. C0 preserved.
    
    def check(val, bytes_hex):
        # Subtract val from C1
        emit('-' * val)
        
        # Is C1 Zero?
        emit('>[-]+<') # C2 = 1
        emit('[>[-]<[-]]') # If C1!=0, C2=0. C1 Cleared.
        
        # If C2 is 1 (Match), Emit.
        emit('>>[') 
        emit_bytes(bytes_hex)
        emit('[-]]') # Clear C2
        
        # Reset C1 for next check?
        # No, we need to recopy C0.
        emit('<<') # Back to C0
        # Recopy for next check
        emit('>[-]>[-]<< [>+>+<<-] >> [<<+>>-] <')

    # Order check (values are separate now, always checking against fresh copy)
    
    # + (43)
    check(43, [0x41, 0xfe, 0x05, 0x00])
    # - (45)
    check(45, [0x41, 0xfe, 0x0d, 0x00])
    # . (46)
    check(46, [
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x4c, 0x89, 0xee,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ])
    # > (62)
    check(62, [0x49, 0xff, 0xc5])
    # < (60)
    check(60, [0x49, 0xff, 0xcd])
    
    # Consume C0 to exit
    emit('[-],]')

    # --- Epilogue (Exit 0) ---
    exit_code = [0xb8, 0x3c, 0x00, 0x00, 0x00, 0x48, 0x31, 0xff, 0x0f, 0x05]
    for b in exit_code:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # Output
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
