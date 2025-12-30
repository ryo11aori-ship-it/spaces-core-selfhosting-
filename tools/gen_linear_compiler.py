import sys

# Stage 9: Linear Native Compiler Generator (With Padding Fix)
# Generates a Spaces program that:
# 1. Emits ELF Header (Claiming 16KB size).
# 2. Translates Source to Machine Code.
# 3. PADS the output with zeros to satisfy the 16KB header claim.

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
        0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # FileSize (0x4000 = 16KB)
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
    
    def emit_bytes(bs):
        for b in bs:
            emit('>' + '+'*b + '. [-] <')

    # Copy C0 -> C1 safely
    emit('>[-]>[-]<< [>+>+<<-] >> [<<+>>-] <') 
    
    # Check function
    def check(val, bytes_hex):
        emit('-'*val) # Sub val from C1
        emit('>[-]+<') # Set C2=1
        emit('[>[-]<[-]]') # If C1!=0, Clear C2 & C1
        
        emit('>') # To C2 (Flag)
        emit('[') 
        emit_bytes(bytes_hex)
        emit('[-]]') # Clear C2
        
        emit('<<') # To C0
        emit('>[-]>[-]<< [>+>+<<-] >> [<<+>>-] <') # Recopy C0->C1

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
    # We claimed FileSize is 0x4000 (16384 bytes).
    # We must emit enough zeros to ensure the file is at least that big.
    # We will simply emit 16KB of zeros blindly.
    
    # Strategy: 
    # Use C2 as counter. Set to 64.
    # Inner loop: Print 0 (from C3) 256 times.
    # 64 * 256 = 16384 bytes.
    
    emit('>>') # Move to C2
    emit('[-]' + '+'*64) # C2 = 64
    emit('[')
    emit('>') # Move to C3 (Clean 0)
    emit('.' * 256) # Print 0, 256 times
    emit('<') # Back to C2
    emit('-]') # Dec C2
    
    # Output
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))

if __name__ == "__main__":
    main()
