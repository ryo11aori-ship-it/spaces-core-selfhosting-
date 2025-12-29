import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Fixed: Pointer movement bug (returning from Flag cell to Char cell).

def main():
    bf = []
    
    def emit(s): bf.append(s)
    
    # --- 1. Header (SPA\x03) ---
    # Use Cell 0 for Output Temp initially
    # Output S P A \x03
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')
    emit('+' * 0x03); emit('.'); emit('[-]')

    # --- 2. Main Loop ---
    # Cell 0: Input Char
    emit(',')
    emit('[') 

    # Logic:
    # Cell 0: Char (Residual)
    # Cell 1: Temp (for copying)
    # Cell 2: Work (for checking)
    # Cell 3: Flag (Result)

    def check_and_out(delta, out_opcode):
        # 1. Subtract delta from Cell 0
        emit('-' * delta)
        
        # 2. Copy Cell 0 to Cell 2 using Cell 1 as temp
        # Start at 0.
        emit('>[-]>[-]<<') # Clear 1, 2
        emit('[>+>+<<-]>>[<<+>>-]<<') # Copy 0->1->0&2. Result: 0=Char, 1=0, 2=Char
        
        # 3. Check if Cell 2 is 0
        emit('>>') # Go to 2
        emit('[-]+<') # Clear 2, Set 2=1 (Wait, simplified check logic below)
        
        # Check Zero Logic on Cell 2:
        # We want Flag (Cell 3) = 1 if Cell 2 == 0.
        # Set Flag=1. If Cell 2 != 0, Set Flag=0.
        
        emit('>[-]+') # Set Cell 3 (Flag) = 1
        emit('<') # Back to Cell 2
        emit('[>-<[-]]') # If Cell 2!=0, Dec Flag, Clear Cell 2.
        
        # 4. If Flag (Cell 3) is 1, Output
        emit('>') # Go to Cell 3
        emit('[')
        # MATCHED!
        # Reuse Cell 3 for output (Clear Flag first)
        emit('[-]') 
        emit('+' * out_opcode)
        emit('.')
        emit('[-]')
        emit(']')
        
        # 5. Return to Cell 0
        # We are at Cell 3.
        emit('<<<') # 3 -> 0

    # Chain of Checks (Sorted by ASCII value)
    # + (43) -> Op 3
    check_and_out(43, 3)
    # , (44) -> Op 6 (Delta 1)
    check_and_out(1, 6)
    # - (45) -> Op 4 (Delta 1)
    check_and_out(1, 4)
    # . (46) -> Op 5 (Delta 1)
    check_and_out(1, 5)
    # < (60) -> Op 2 (Delta 14)
    check_and_out(14, 2)
    # > (62) -> Op 1 (Delta 2)
    check_and_out(2, 1)
    # [ (91) -> Op 7 (Delta 29)
    check_and_out(29, 7)
    # ] (93) -> Op 8 (Delta 2)
    check_and_out(2, 8)

    # Done checking. Clear Cell 0
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
