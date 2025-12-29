import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Fixed: Adjusted logic to fix output character shift bug.

def main():
    bf = []
    
    def emit(s): bf.append(s)
    
    # --- 1. Header (SPA\x03) ---
    # Use Cell 0 for Output Temp
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')
    emit('+' * 0x03); emit('.'); emit('[-]')

    # --- 2. Main Loop ---
    # Cell 0: Input Char
    emit(',')
    emit('[') 

    # Logic Structure:
    # Cell 0: Char (Residual value from progressive subtraction)
    # Cell 1: Temp (Copy of Char for checking)
    # Cell 2: Flag (1 if Match, 0 if No Match) / Temp for Copy

    def check_and_out(delta, out_opcode):
        # 1. Subtract delta from Cell 0
        emit('-' * delta)
        
        # 2. Copy Cell 0 to Cell 1 (Destructive to Cell 0, so use Cell 2 to restore)
        # Start at 0.
        emit('>[-]>[-]<<')           # Clear 1, 2. Ptr=0
        emit('[>+>+<<-]')            # Move 0 -> 1, 2. Ptr=0
        emit('>>[<<+>>-]')           # Move 2 -> 0. Ptr=2 (Loop ends at source)
        emit('<<')                   # Ptr=0
        
        # 3. Check Cell 1. If 0, Set Flag (Cell 2) = 1.
        # We are at 0. Go to 2.
        emit('>>[-]+')               # Flag(2) = 1. Ptr=2
        emit('<')                    # Ptr=1
        emit('[>-<[-]]')             # If 1!=0, Flag(2)=0, Clear 1. Ptr=1
        
        # 4. Action based on Flag (Cell 2)
        emit('>')                    # Ptr=2
        emit('[')                    # If Flag=1 (Match)
        emit('[-]')                  # Clear Flag
        emit('>' + ('+'*out_opcode)) # Use Cell 3 for output val
        emit('.')                    # Output
        emit('[-]<')                 # Clear Cell 3, Back to 2
        emit(']')
        
        # 5. Return to Cell 0
        emit('<<')                   # 2 -> 0

    # Chain of Checks (Sorted by ASCII value)
    # The previous logic had a slight off-by-one or order issue.
    # Let's verify the ASCII values and deltas carefully.
    # + (43)
    # , (44) -> Delta 1
    # - (45) -> Delta 1
    # . (46) -> Delta 1
    # < (60) -> Delta 14
    # > (62) -> Delta 2
    # [ (91) -> Delta 29
    # ] (93) -> Delta 2

    # Opcode Mapping (vm.c logic):
    # > : 0x01
    # < : 0x02
    # + : 0x03
    # - : 0x04
    # . : 0x05
    # , : 0x06
    # [ : 0x07
    # ] : 0x08

    # Apply checks
    check_and_out(43, 3) # + (43) -> Op 3
    check_and_out(1, 6)  # , (44) -> Op 6
    check_and_out(1, 4)  # - (45) -> Op 4
    check_and_out(1, 5)  # . (46) -> Op 5
    check_and_out(14, 2) # < (60) -> Op 2
    check_and_out(2, 1)  # > (62) -> Op 1
    check_and_out(29, 7) # [ (91) -> Op 7
    check_and_out(2, 8)  # ] (93) -> Op 8

    # Done checking. Cell 0 is residual junk. Clear it.
    emit('[-]')
    
    # Read Next
    emit(',')
    emit(']')

    # Convert to Spaces
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    
    full_bf = "".join(bf)
    print("".join([mapping.get(c, '') for c in full_bf]), end='')

if __name__ == "__main__":
    main()
