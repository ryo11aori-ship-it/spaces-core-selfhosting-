import sys

# Stage 9: Linear Native Compiler Generator (Fixed Logic)
# Generates a Spaces program that:
# 1. Emits ELF Header.
# 2. Reads ASCII BF source from stdin.
# 3. Translates into x64 Machine Code using a correct "Copy & Check" strategy.
# 4. Emits Footer (Exit syscall).

def main():
    bf = []
    def emit(s): bf.append(s)

    # --- ELF Header (x86-64 Linux) ---
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

    # --- Main Compilation Loop ---
    emit(',[') 
    
    # Helper to emit bytes
    # Assumes we are at C2 (Flag). Uses C3 as scratch.
    def emit_bytes(bs):
        for b in bs:
            emit('>' + '+'*b + '. [-] <')

    # Copy C0 -> C1 safely
    # Start: C0. End: C1.
    emit('>[-]>[-]<< [>+>+<<-] >> [<<+>>-] <') 
    
    # Check function (Corrected Pointer Logic)
    def check(val, bytes_hex):
        # We are at C1 (Value Copy).
        # Subtract val from C1
        emit('-'*val)
        
        # Is C1 Zero? Use C2 as Flag.
        emit('>[-]+<') # Set C2=1. Return to C1.
        emit('[>[-]<[-]]') # If C1!=0, Clear C2, Clear C1. End at C1.
        
        # Move to Flag (C2)
        emit('>') 
        # If C2 is 1 (Match), Emit.
        emit('[') 
        emit_bytes(bytes_hex)
        emit('[-]]') # Clear C2.
        
        # We are at C2. Restore Logic expects to be at C0.
        emit('<<') 
        # Recopy C0 to C1 for next check. End at C1.
        emit('>[-]>[-]<< [>+>+<<-] >> [<<+>>-] <')

    # Order check
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
    
    # Consume C0 (Input) to exit loop
    # We are at C1. Go to C0.
    emit('< [-],]')

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
