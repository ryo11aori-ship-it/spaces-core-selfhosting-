import sys

def main():
    # Brainfuck/Spaces Generator Helpers
    def move(n): return ">"*n if n>0 else "<"*abs(n)
    def add(n): return "+"*n
    def sub(n): return "-"*n
    def loop(content): return "[" + content + "]"
    
    # ---------------------------------------------------------
    # Logic: Linear Interpreter
    # Layout: [Temp][InputChar][VirtualTape...]
    # We treat Cell 0 as Temp, Cell 1 as Input Buffer.
    # Virtual Tape starts at Cell 2.
    # ---------------------------------------------------------
    
    bf = ""
    
    # 1. Skip Header (Read 3 bytes: S, P, A)
    # We assume valid input for Stage 2 to keep logic simple.
    bf += move(1) + "," + "," + "," # Read 3 bytes into Cell 1 and discard
    
    # 2. Main Fetch-Decode-Execute Loop
    # Cell 1 holds the current Opcode.
    bf += "," # Read first opcode
    bf += loop(
        # We are at Cell 1 (Opcode)
        
        # Check 0x01 (>) PTR_INC ? (Not impl in linear simple version)
        # Check 0x02 (<) PTR_DEC ? (Not impl in linear simple version)
        
        # Check 0x03 (+) VAL_INC
        sub(3) # 0x03 -> 0
        + loop( # If not 0 (it wasn't +)
            sub(1) # Check 0x04 (-)
            + loop( # If not 0 (it wasn't -)
                sub(1) # Check 0x05 (.)
                + loop( # If not 0 (it wasn't .)
                     # Unknown or unimplemented op, just clear it to exit inner checks
                     clear() 
                )
                # --- CASE: . (Output) ---
                # Logic: Output value at Virtual Tape (Cell 2)
                + move(1) + "." + move(-1) 
                + clear() # Exit logic
            )
            # --- CASE: - (Dec) ---
            # Logic: Dec Virtual Tape (Cell 2)
            + move(1) + sub(1) + move(-1)
            + clear()
        )
        # --- CASE: + (Inc) ---
        # Logic: Inc Virtual Tape (Cell 2)
        + move(1) + add(1) + move(-1)
        
        # Read Next Opcode
        + ","
    )

    # ---------------------------------------------------------
    # Convert BF to Spaces
    # ---------------------------------------------------------
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    
    def clear(): return "[-]"
    
    # Re-map the simplified logic above to full mapping
    res = ""
    for c in bf:
        if c in mapping: res += mapping[c]
    
    print(res, end='')

if __name__ == "__main__":
    main()
