import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Fixed: Switched to Non-Progressive (Absolute) checks to eliminate cumulative errors.

def main():
    bf = []
    
    def emit(s): bf.append(s)
    
    # --- 1. Header (SPA\x03) ---
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')
    emit('+' * 0x03); emit('.'); emit('[-]')

    # --- 2. Main Loop ---
    # Cell 0: Input Char
    emit(',')
    emit('[') 

    # Logic Structure:
    # Cell 0: Char (Preserved)
    # Cell 1: Temp (Copy of Char for checking)
    # Cell 2: Backup (To restore Cell 0)
    # Cell 3: Flag / Output

    def check_and_out(ascii_val, out_opcode):
        # 1. Copy Cell 0 to Cell 1 and Cell 2
        #    Cell 0 is cleared in process, then restored from Cell 2 later.
        emit('>[-]>[-]<<')           # Clear 1, 2. Ptr=0
        emit('[>+>+<<-]')            # Move 0 -> 1, 2. Ptr=0
        
        # 2. Subtract ascii_val from Cell 1
        emit('>')                    # Ptr=1
        emit('-' * ascii_val)
        
        # 3. Check Cell 1. If 0, Set Flag (Cell 3) = 1.
        #    (We use Cell 3 as Flag to avoid messing up Cell 2)
        emit('>>[-]+')               # Flag(3) = 1. Ptr=3
        emit('<<')                   # Ptr=1
        emit('[>>-<<[-]]')           # If 1!=0, Flag(3)=0, Clear 1. Ptr=1
        
        # 4. Action based on Flag (Cell 3)
        emit('>>')                   # Ptr=3
        emit('[')                    # If Flag=1 (Match)
        emit('[-]')                  # Clear Flag
        emit('+' * out_opcode)       # Set Output
        emit('.')                    # Output
        emit('[-]')                  # Clear Output
        emit(']')
        
        # 5. Restore Cell 0 from Cell 2
        emit('<')                    # Ptr=2
        emit('[<<+>>-]')             # Move 2 -> 0. Ptr=2
        emit('<<')                   # Ptr=0

    # Absolute Checks (Order doesn't matter, but sorted is nice)
    check_and_out(43, 3) # +
    check_and_out(44, 6) # ,
    check_and_out(45, 4) # -
    check_and_out(46, 5) # .
    check_and_out(60, 2) # <
    check_and_out(62, 1) # >
    check_and_out(91, 7) # [
    check_and_out(93, 8) # ]

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
