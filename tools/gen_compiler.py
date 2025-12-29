import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Fixed: Strict pointer arithmetic to prevent Segfault (Cell -1 access).

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

    # Logic:
    # Cell 0: Char (Residual)
    # Cell 1: Temp
    # Cell 2: Check Copy
    # Cell 3: Flag / Output

    def check_and_out(delta, out_opcode):
        # 1. Subtract delta from Cell 0
        emit('-' * delta)
        
        # 2. Copy Cell 0 to Cell 2 using Cell 1 as temp
        # Start at 0.
        emit('>[-]>[-]<<') # Clear 1, 2. Return to 0.
        emit('[>+>+<<-]>>[<<+>>-]<<') # Copy 0->1->0&2. Return to 0.
        
        # 3. Check if Cell 2 is 0
        # Go to Cell 3 (Flag), Set to 1
        emit('>>>') # 0 -> 3
        emit('[-]+') # Flag = 1
        emit('<') # 3 -> 2
        
        # If Cell 2 is NOT 0: Clear Flag (3) and Clear Cell 2
        emit('[>[-]<[-]]')
        
        # Now we are at Cell 2 (which is 0).
        
        # 4. Check Flag at Cell 3
        emit('>') # 2 -> 3
        emit('[')
        # MATCHED!
        emit('[-]') # Clear Flag
        emit('+' * out_opcode)
        emit('.')
        emit('[-]') # Clear Output
        emit(']')
        
        # 5. Return to Cell 0
        # We are currently at Cell 3.
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
