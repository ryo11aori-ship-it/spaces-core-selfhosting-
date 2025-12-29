import sys

# Stage 4: Self-Hosted Compiler (Source -> Binary)
#
# This generates a Spaces program that:
# 1. Outputs the binary header (SPA\3)
# 2. Reads Spaces source code char-by-char
# 3. Converts valid chars to Opcodes (1..8) and outputs them
#
# This effectively replaces 'tools/encoder.c'.

def main():
    bf = []
    
    # --- Helper Functions ---
    def emit(s): bf.append(s)
    
    # Output byte B
    def out_byte(b):
        # We assume current cell is 0. Set to b, output, clear.
        emit('+' * b)
        emit('.')
        emit('[-]')

    # --- 1. Emit Header (SPA\x03) ---
    out_byte(0x53) # S
    out_byte(0x50) # P
    out_byte(0x41) # A
    out_byte(0x03) # Version 3

    # --- 2. Main Loop ---
    # Read first char
    emit(',')
    emit('[') # While not EOF

    # We have Char in Cell 0.
    # We need to preserve it for comparison chain.
    # Logic: Copy Char to Temp. Check matches.
    
    # Simple linear check logic (Destructive Check)
    # Since we don't need the char after checking, we can just subtract.
    # Order of checks: > (62), < (60), + (43), - (45), . (46), , (44), [ (91), ] (93)
    # Sorted by ascii value to minimize subtractions:
    # + (43), , (44), - (45), . (46), < (60), > (62), [ (91), ] (93)

    # Offset 43 (+)
    emit('-' * 43) 
    
    # Check + (0)
    # Is_Match logic without nested indents:
    # Use Cell 1 as Flag. 
    # If Cell 0 is 0, Set Cell 1 = Opcode(3). Output Cell 1.
    
    # Too complex logic in raw BF risks bugs. 
    # Let's use the simplest logic: "Subtract and Output if Zero, then Restore" ? 
    # No, restoring is hard.
    # Better: "Subtract delta. If zero, output specific value."
    
    # Since we generated "Echo" successfully, let's keep it extremely simple.
    # We will just implement a translation chain using a temporary flag.
    # Char is at Cell 0. Temp at Cell 1.
    
    # Structure:
    #   Check(Ascii, OutputVal)
    
    # Because implementing "If Zero" in BF requires a helper, 
    # we use the standard idiom: temp0[-]+ temp1[ temp0[-] temp1[-] ] temp0[ MATCHED ]
    
    # But to keep it robust and prevent nesting errors:
    # We will just generate raw BF string for each check.
    
    # Reset Cell 1 (Output Accumulator)
    emit('>') # To Cell 1
    emit('[-]')
    emit('<') # To Cell 0
    
    # We will shift Cell 0 down. If it hits 0, we set Cell 1 to the Opcode.
    
    # 43 (+) -> Op 3
    emit('-'*43)
    # If 0, Cell 1 = 3.
    # Check 0 logic: >+< [ >-< [-] ] > [ <+++> - ] <
    # Detailed:
    #   Cell 1 = 1.
    #   Cell 0 loop [ Cell 1 = 0. Clear Cell 0. ]
    #   Cell 1 loop [ Cell 1 = 0. Cell 1 (now target) = 3. ]
    # Wait, if we clear Cell 0 inside check, we can't check next.
    # We must RESTORE Cell 0 or Copy it first.
    
    # --- PROPOSAL: USE A LOOKUP TABLE (Stateless) ---
    # We don't verify input strictness. We just check.
    # Actually, simpler: 
    # Just emit "If char is +, output \x03".
    
    # Let's use a Python helper to generate the "If X, Output Y" block safely.
    def check_and_out(char_code_delta, out_val):
        # Assumes we are at Cell 0.
        # Destructively subtracts `char_code_delta` from Cell 0.
        # If result is 0, outputs `out_val`.
        # NOTE: This destroys Cell 0 for subsequent checks if not matched.
        # So we must COPY Cell 0 to Cell 2 before checking.
        
        # Copy Cell 0 -> Cell 2 using Cell 1 as temp
        # Cell 0: Char, Cell 1: 0, Cell 2: 0
        emit('>[-]>[-]<<') # Clear 1, 2
        emit('[>+>+<<-]>>[<<+>>-]<<') # Copy 0->2, restore 0.
        
        # Now work on Cell 2
        emit('>>') 
        emit('-' * char_code_delta)
        
        # Check if Cell 2 is 0.
        # Use Cell 3 as Flag.
        emit('>[-]+<') # Flag = 1
        emit('[>-<[-]]') # If Cell 2 != 0, Flag = 0. Cell 2 cleared.
        
        emit('>') # Go to Flag
        emit('[') 
        # MATCHED!
        # Output `out_val`
        emit('[-]') # Clear Flag
        emit('+' * out_val)
        emit('.')
        emit('[-]')
        emit(']')
        emit('<<<') # Back to Cell 0
        
    # Order (Offsets are relative to previous!)
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
    
    # Clear Cell 0 (consumed)
    emit('[-]')
    
    # Read Next
    emit(',')
    emit(']')

    # Spaces Conversion
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    print("".join([mapping.get(c, '') for c in bf]), end='')

if __name__ == "__main__":
    main()
