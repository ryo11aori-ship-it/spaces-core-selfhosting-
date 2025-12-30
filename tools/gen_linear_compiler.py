import sys

# Stage 9: Linear Native Compiler Generator (Alignment Fix)
# Generates a Spaces program that:
# 1. Emits ELF Header with SAFE Alignment (4KB).
# 2. Translates Source to Machine Code.
# 3. PADS the output to ensure it covers the declared FileSize.

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
        # FIX 1: Set FileSize to 0x1000 (4KB). Small and safe.
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        # MemSize (8MB)
        0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 
        # FIX 2: Set Alignment to 0x1000 (4KB). Previous 0x200000 (2MB) was too aggressive.
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
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
    
    def emit_bytes(bs):
        for b in bs:
            emit('>' + '+'*b + '. [-] <')

    # Copy C0 -> C1 safely
    emit('>[-]>[-]<< [>+>+<<-] >> [<<+>>-] <') 
    
    # Check function (Correct Logic)
    def check(val, bytes_hex):
        emit('-'*val) # Sub val from C1
        emit('>[-]+<') # Set C2=1
        emit('[>[-]<[-]]') # If C1!=0, Clear C2 & C1
        emit('>') # To C2
        emit('[') 
        emit_bytes(bytes_hex)
        emit('[-]]') # Clear C2
        emit('<<') # To C0
        emit('>[-]>[-]<< [>+>+<<-] >> [<<+>>-] <') # Recopy

    # Order check
    check(43, [0x41, 0xfe, 0x05, 0x00]) # +
    check(45, [0x41, 0xfe, 0x0d, 0x00]) # -
    check(46, [
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x4c, 0x89, 0xee,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]) # .
    check(62, [0x49, 0xff, 0xc5]) # >
    check(60, [0x49, 0xff, 0xcd]) # <
    
    emit('< [-],]') # Consume C0, loop

    # --- Epilogue (Exit 0) ---
    exit_code = [0xb8, 0x3c, 0x00, 0x00, 0x00, 0x48, 0x31, 0xff, 0x0f, 0x05]
    for b in exit_code:
        if b: emit('+'*b + '. [-]')
        else: emit('.')

    # --- PADDING FIX ---
    # We claimed FileSize is 0x1000 (4096 bytes).
    # We emit 4096 zeros to ensure the file is at least that big.
    # Code is usually ~2800 bytes. 2800 + 4096 > 4096. Safe.
    
    emit('>>') # To C2
    emit('[-]' + '+'*16) # C2 = 16
    emit('[')
    emit('>') # To C3
    emit('.' * 256) # Print 256 zeros
    emit('<') # To C2
    emit('-]') # Dec C2
    # 16 * 256 = 4096 bytes padding.

    # Output
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
