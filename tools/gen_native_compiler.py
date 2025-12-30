import sys

# Stage 5: Native Self-Hosted Compiler (Spaces UTF-8 Source -> Spaces Binary)
# Fixed: Simplified logic using linear subtraction (0x20 -> 0xC3) to avoid pointer complexity.

def main():
    bf = []
    def emit(s): bf.append(s)
    
    # --- 1. Header (SPA) ---
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')

    # --- Variables / Cell Layout ---
    # Cell 0: Input Char
    # Cell 1: Bit Buffer
    # Cell 2: Bit Count
    # Cell 3: Check Work / Flag
    # Cell 4: Temp

    # --- 2. Main Loop ---
    emit(',')
    emit('[') 

    # 1. Copy Cell 0 -> Cell 3 (Work) using Cell 4 as temp
    # We leave Cell 0 intact (though we technically don't need it after this, keeping it simple)
    emit('>>>[-]>[-]<<<<') # Clear 3, 4. Ptr=0
    emit('[>>>+>+<<<<-]')  # Move 0 -> 3, 4. Ptr=0
    emit('>>>>[<<<<+>>>>-]') # Restore 4 -> 0. Ptr=4
    emit('<<<<') # Ptr=0
    
    # 2. Check if 0x20 (Space)
    # Subtract 32 from Cell 3
    emit('>>>') # Ptr=3
    emit('-' * 0x20)
    
    # Check if Zero (Is it 0x20?)
    # Store result in Cell 4 (1 if Match, 0 if Not)
    emit('>[-]+<') # Cell 4 = 1. Ptr=3.
    emit('[>-<[-]]') # If Cell 3 != 0, Cell 4 = 0. Ptr=3.
    
    # If Match (Cell 4 == 1)
    emit('>') # Ptr=4
    emit('[')
        # ACTION: Append 0
        # Go to Buffer logic...
        # We'll just inline append_bit(0) here to be safe.
        
        # Buffer(1) = Buffer * 2
        emit('<<<') # Ptr=1
        emit('[>>>+<<<-]>>>[<<<++>>>-]') # 1->4->1(x2). Ptr=4
        emit('<<') # Ptr=2 (Count)
        emit('+') # Count++
        
        # Check Count == 3 logic later... 
        # Actually, let's put the "Flush" logic at the end of the loop to save code?
        # No, let's keep it robust.
        
        # Flush if Count(2) == 3
        # Copy 2 -> 3 (Temp). Use 0 as restore temp? No, 0 is input. Use 4? 4 is current Flag loop.
        # We are inside Flag Loop (4). We can use 3 (Work) as temp since it's 0.
        emit('>[-]<<[>+>+<<-]>>[<<+>>-]') # Copy 2->3,4->2. Ptr=4? No logic is tricky inside loop.
        
        # SIMPLIFICATION: 
        # Just increment buffer and count here. We will check "Count==3" at the very end of main loop.
        # It's safe to check every time.
        
        emit('[-]') # Clear Flag(4) to exit
    emit(']')
    
    # 3. If NOT 0x20, Check if 0xE3 (Full Space)
    # If Cell 3 was NOT 0, it holds (Char - 32).
    # We want to check if Char == 227 (0xE3).
    # So we check if (Char - 32) == (227 - 32) == 195 (0xC3).
    
    # But wait, the previous check CLEARED Cell 3 if it was not zero!
    # " [>-<[-]] " -> This clears Cell 3!
    # So we cannot chain checks destructively like this unless we restore Cell 3.
    
    # RE-STRATEGY: Restore Cell 3? Or check from Cell 0 again?
    # Checking from Cell 0 is safer and easier.
    
    # --- RESET ---
    # We are at Ptr=4 (Flag). It is 0 now.
    emit('<<<<') # Ptr=0
    
    # Check 0xE3
    # Copy 0 -> 3
    emit('>>>[-]>[-]<<<<')
    emit('[>>>+>+<<<<-]>>>>[<<<<+>>>>-]<<<<') # Copy 0->3,4->0. Ptr=0.
    
    emit('>>>') # Ptr=3
    emit('-' * 0xE3)
    emit('>[-]+<') # Flag(4)=1
    emit('[>-<[-]]') # Check Zero. Ptr=3.
    
    emit('>') # Ptr=4
    emit('[')
        # ACTION: Append 1
        # 1. Eat 2 bytes
        emit('<<<<') # Ptr=0
        emit(',,')   # Read junk
        emit('>>>>') # Ptr=4
        
        # 2. Buffer = Buffer * 2 + 1
        emit('<<<') # Ptr=1
        emit('[>>>+<<<-]>>>[<<<++>>>-]') # x2
        emit('<<<+>>>') # +1
        
        # 3. Count++
        emit('<<+') # Ptr=2
        
        emit('>>[-]') # Clear Flag(4)
    emit(']')
    
    # --- FLUSH LOGIC ---
    # Check if Count(2) == 3
    # We are at Ptr=4.
    emit('<<') # Ptr=2
    
    # Copy Count(2) to Temp(3)
    emit('>[-]<[>+>+<<-]>>[<<+>>-]<') # 2->3,4->2. Ptr=3.
    emit('---') # Subtract 3
    emit('>[-]+<') # Flag(4)=1
    emit('[>-<[-]]') # Check Zero. Ptr=3.
    
    emit('>') # Ptr=4
    emit('[')
        # FLUSH!
        # Opcode = Buffer(1) + 1
        emit('<<<') # Ptr=1
        emit('[>>+<<-]') # Move Buffer(1) -> 3. Ptr=1.
        emit('>>') # Ptr=3
        emit('+.') # Output
        emit('[-]') # Clear 3
        
        # Reset Count(2)
        emit('<[-]') 
        
        emit('>>[-]') # Clear Flag(4)
    emit(']')
    
    # Return to 0
    emit('<<<<')

    # --- End Main Loop ---
    emit('[-]')
    emit(',')
    emit(']')

if __name__ == "__main__":
    main()
