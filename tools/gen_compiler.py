import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Fixed: Proper cell allocation to prevent destroying the input character backup.

def main():
    bf = []
    
    def emit(s): bf.append(s)
    
    # --- 1. Header (SPA\x03) ---
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')
    emit('+' * 0x03); emit('.'); emit('[-]')

    # --- 2. Main Loop ---
    emit(',')
    emit('[') 

    # Cell Layout:
    # Cell 0: Char (Main)
    # Cell 1: Temp (Subtraction target)
    # Cell 2: Backup (ReadOnly copy of Char)
    # Cell 3: Flag (Check Result)

    def check_and_out(ascii_val, out_opcode):
        # 1. Copy Cell 0 -> Cell 1 and Cell 2
        #    We must clear 1 and 2 first.
        emit('>[-]>[-]<<')           # Clear 1, 2. Ptr=0
        emit('[>+>+<<-]')            # Move 0 -> 1, 2. Ptr=0
        
        # 2. Subtract ascii_val from Cell 1
        emit('>')                    # Ptr=1
        emit('-' * ascii_val)
        
        # 3. Check Cell 1. Use Cell 3 as Flag.
        emit('>>[-]+')               # Ptr=3. Flag=1.
        emit('<<')                   # Ptr=1
        emit('[>>-<<[-]]')           # If Cell 1 != 0, Flag(3)=0, Clear 1. Ptr=1
        
        # 4. Action based on Flag (Cell 3)
        emit('>>')                   # Ptr=3
        emit('[')                    # If Flag=1 (Match)
        emit('[-]')                  # Clear Flag
        emit('+' * out_opcode)       # Set Output Value
        emit('.')                    # Output
        emit('[-]')                  # Clear Output
        emit(']')
        
        # 5. Restore Cell 0 from Cell 2 (Backup)
        #    Cell 2 still holds the original char. Move it back to 0.
        emit('<')                    # Ptr=2
        emit('[<<+>>-]')             # Move 2 -> 0. Ptr=2
        emit('<<')                   # Ptr=0

    # Absolute Checks (Sorted by ASCII value)
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
