import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Fixed: Uses progressive subtraction on the main char cell.

def main():
    bf = []
    
    def emit(s): bf.append(s)
    
    # --- 1. Header (SPA\x03) ---
    # Use Cell 0 for Output Temp initially
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')
    emit('+' * 0x03); emit('.'); emit('[-]')

    # --- 2. Main Loop ---
    # Cell 0: Input Char
    emit(',')
    emit('[') 

    # Logic:
    # Cell 0 holds the input char. We subtract progressively.
    # Cells used: 
    # 0: Char (Residual value)
    # 1: Temp (Copy for checking)
    # 2: Flag (Check result)
    # 3: Output Value

    def check_and_out(delta, out_opcode):
        # 1. Subtract delta from Cell 0 (Progressive)
        emit('-' * delta)
        
        # 2. Copy Cell 0 to Cell 1 to check if it reached 0
        # (We must preserve Cell 0 for the next check in the chain)
        emit('>[-]>[-]<<') # Clear 1, 2
        emit('[>+>+<<-]>>[<<+>>-]<<') # Copy 0->1, using 2 as temp
        
        # 3. Check if Cell 1 is 0
        # Set Flag (Cell 2) = 1
        emit('>>[-]+<') 
        # If Cell 1 is not 0, set Flag = 0 and clear Cell 1
        emit('[>-<[-]]')
        
        # 4. If Flag (Cell 2) is 1, Output Opcode
        emit('>') # To Cell 2
        emit('[')
        # MATCHED!
        emit('>') # Cell 3
        emit('+' * out_opcode)
        emit('.')
        emit('[-]')
        emit('<') # Back to Cell 2
        emit('[-]') # Clear Flag
        emit(']')
        emit('<<') # Back to Cell 0

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

    # Done checking. Cell 0 is now garbage (Input - 93).
    # Clear Cell 0
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
