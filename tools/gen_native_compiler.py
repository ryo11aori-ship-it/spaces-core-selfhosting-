import sys

# Stage 5: Native Self-Hosted Compiler (Spaces UTF-8 Source -> Spaces Binary)
# Features:
# - Reads UTF-8 stream.
# - Parses Space (0x20) as bit 0.
# - Parses Ideographic Space (0xE3..) as bit 1.
# - Aggregates 3 bits -> 1 Opcode.

def main():
    bf = []
    def emit(s): bf.append(s)
    
    # --- 1. Header (SPA) ---
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')
    # Note: No version byte, to match VM logic (starts reading at byte 3)

    # --- Variables / Cell Layout ---
    # Cell 0: Input Char
    # Cell 1: Bit Buffer (accumulates bits)
    # Cell 2: Bit Count (0..3)
    # Cell 3: Temp / Copy
    # Cell 4: Flag
    
    # --- 2. Main Loop ---
    emit(',')
    emit('[') 

    # We need to detect 0x20 (Space) or 0xE3 (Start of Full Space)
    # Other chars are ignored (newlines, etc.)

    # Helper: Check if Cell 0 == val. Result in Cell 4.
    def check_val(val):
        # Copy 0 -> 3 (Temp)
        emit('>[-]>[-]<<') # Clear 3, 4. Ptr=0
        emit('[>>>+<<<-]>>>[<<<+>>>-]<<<') # Copy 0->3, restore 0. Ptr=0
        
        # Subtract val from 3
        emit('>>>') # Ptr=3
        emit('-' * val)
        
        # Check if 3 is 0. Result in 4.
        emit('>[-]+<') # Flag(4)=1. Ptr=3
        emit('[>-<[-]]') # If 3!=0, Flag(4)=0, Clear 3.
        emit('<') # Ptr=2 (Back closer to home)
        emit('<<') # Ptr=0

    # Helper: Append Bit (0 or 1)
    def append_bit(bit_val):
        # We are at Ptr=0.
        # Buffer is at Cell 1. Count is at Cell 2.
        
        # Buffer = Buffer * 2 + bit_val
        emit('>') # Ptr=1 (Buffer)
        emit('[>>>+<<<-]>>>') # Move Buffer->4(Temp)
        emit('[<<<++>>>-]')   # Move 4->1 (Doubled)
        if bit_val == 1:
            emit('<<<+>>>')    # Add 1 to Buffer
        emit('<<<') # Ptr=1
        
        # Count++
        emit('>') # Ptr=2 (Count)
        emit('+')
        
        # Check if Count == 3
        # Copy Count(2) -> Temp(3)
        emit('>[-]<<[>>+>+<<<-]>>>[<<<+>>>-]') # Copy 2->3. Ptr=3
        emit('---') # Subtract 3
        
        # Check if 0. Flag in 4.
        emit('>[-]+<') # Flag(4)=1
        emit('[>-<[-]]') # If !=0, Flag=0.
        
        # If Flag(4) is 1, Output Opcode
        emit('>') # Ptr=4
        emit('[') 
        # Output Logic: Opcode = Buffer + 1
        # Buffer is at 1. Copy to 3(Temp) for output.
        emit('<<<') # Ptr=1
        emit('[>>+>+<<<-]>>>[<<<+>>>-]') # Copy 1->3
        emit('<') # Ptr=3 (Temp)
        emit('+.') # Add 1 and Output
        emit('[-]') # Clear Output
        
        # Reset Buffer(1) and Count(2)
        emit('<<[-]<[-]') # Clear 2, Clear 1
        
        # Clear Flag(4) to exit loop
        emit('>>>[-]') 
        emit(']')
        
        # Return to 0
        emit('<<<<')

    # --- Logic Body ---
    
    # 1. Check for Space (0x20) -> Bit 0
    check_val(0x20)
    emit('>>>>') # Ptr=4 (Flag)
    emit('[')
    emit('[-]') # Clear Flag
    emit('<<<<') # Ptr=0
    append_bit(0)
    emit('>>>>') # Ptr=4
    emit(']')
    emit('<<<<') # Ptr=0

    # 2. Check for 0xE3 -> Bit 1 (and consume 2 bytes)
    check_val(0xE3)
    emit('>>>>') # Ptr=4 (Flag)
    emit('[')
    emit('[-]') # Clear Flag
    emit('<<<<') # Ptr=0
    
    # Consume 2 bytes (0x80, 0x80)
    emit(',.,.') # Read and ignore (Debug: emit . to see if we are eating?) No, just ,
    # Wait, simple , is enough.
    # Actually, let's just emit ',' twice to eat the bytes.
    # We assume valid input.
    # emit(',,') # Eat 2 bytes. (Using logic from tools/encoder.c)
    # But wait, 'emit' appends to python list string. 
    # Brainfuck logic: , (read to cell 0)
    emit(',') # Read byte 2 (0x80) -> Cell 0
    emit(',') # Read byte 3 (0x80) -> Cell 0
    
    append_bit(1)
    
    # Restore Cell 0 to 0 (it holds junk from last read)
    emit('[-]')
    
    emit('>>>>') # Ptr=4
    emit(']')
    emit('<<<<') # Ptr=0

    # --- End Main Loop ---
    # Clear Cell 0 (consumed char)
    emit('[-]')
    emit(',')
    emit(']')

if __name__ == "__main__":
    main()
