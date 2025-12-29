import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Fixed: Correctly reads ASCII chars and outputs binary opcodes.

def main():
    bf = []
    
    # --- Helper Functions ---
    def emit(s): bf.append(s)
    
    # Output byte B
    def out_byte(b):
        emit('+' * b)
        emit('.')
        emit('[-]')

    # --- 1. Emit Header (SPA\x03) ---
    out_byte(0x53) # S
    out_byte(0x50) # P
    out_byte(0x41) # A
    out_byte(0x03) # Version 3

    # --- 2. Main Loop ---
    emit(',')
    emit('[') # While not EOF

    # check_and_out function
    # Cell 0: Char, Cell 1: Temp, Cell 2: Work, Cell 3: Flag
    def check_and_out(char_code_delta, out_val):
        # Copy Cell 0 -> Cell 2 using Cell 1 as temp
        emit('>[-]>[-]<<') 
        emit('[>+>+<<-]>>[<<+>>-]<<') 
        
        # Work on Cell 2
        emit('>>') 
        emit('-' * char_code_delta)
        
        # Check if Cell 2 is 0
        emit('>[-]+<') # Flag = 1 at Cell 3
        emit('[>-<[-]]') # If Cell 2 != 0, Flag = 0
        
        emit('>') # Go to Flag
        emit('[') 
        # MATCHED
        emit('[-]') # Clear Flag
        emit('+' * out_val)
        emit('.')
        emit('[-]')
        emit(']')
        emit('<<<') # Back to Cell 0
        
    # Check Chain (Offsets based on ASCII)
    # + (43)
    check_and_out(43, 3)
    # , (44) -> Delta 1
    check_and_out(1, 6)
    # - (45) -> Delta 1
    check_and_out(1, 4)
    # . (46) -> Delta 1
    check_and_out(1, 5)
    # < (60) -> Delta 14
    check_and_out(14, 2)
    # > (62) -> Delta 2
    check_and_out(2, 1)
    # [ (91) -> Delta 29
    check_and_out(29, 7)
    # ] (93) -> Delta 2
    check_and_out(2, 8)
    
    # Clear Cell 0
    emit('[-]')
    
    # Read Next
    emit(',')
    emit(']')

    # Spaces Conversion
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    
    full_bf = "".join(bf)
    print("".join([mapping.get(c, '') for c in full_bf]), end='')

if __name__ == "__main__":
    main()
