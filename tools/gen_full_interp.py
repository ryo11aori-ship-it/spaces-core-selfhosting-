import sys

def main():
    # Helper functions
    def m(n): return ">"*n if n>0 else "<"*abs(n)
    def a(n): return "+"*n
    def s(n): return "-"*n
    def l(c): return "[" + c + "]"
    def clr(): return "[-]"

    # --- Robust Depth-1 Interpreter Logic ---
    # Memory Layout: [Code...] 0 [Temp] [Flag] 0 [Data...]
    
    # Macros for movement
    # to_data: Assumes we are at an Opcode (non-zero). Moves right past 0 to Data.
    to_data = "[>]>>" 
    # to_code: Assumes we are at Data (non-zero or zero). Moves left past 0 to Opcode.
    # Note: Data might be 0, so we rely on the separator structure.
    # Structure: 0 [Flag] [Temp] 0 [CodeEnd]
    # We explicitly move left fixed steps from Data.
    to_code = "<<[<]" 

    bf = ""
    # 1. Skip Header (S, P, A)
    bf += m(1) + ","*3 
    
    # 2. Read Code (until 0)
    # Layout: 0 [Code...] 0
    bf += m(3) + a(1) + l( "," + l( m(1) ) + a(1) + m(-1) + s(1) + m(-1) ) + m(2)
    
    # 3. Execution Loop
    # Go to Code Start
    bf += "<[<]>"
    
    # Main Loop (Iterate over Code)
    bf += "["
    
    # Copy Opcode to Temp for checking
    # Layout: [Op] [Temp]
    bf += l( m(1)+a(1)+m(1)+a(1)+m(-2) ) + m(2) + l(m(-2)+a(1)+m(2)) + m(-2)
    
    # --- SCAN LOGIC (Simplified for Stability) ---
    # scan_fwd: Search for ] (0x08). 
    # Logic: Move Right. Sub 8. If 0, Stop. Else Add 8, Repeat.
    # At end: Add 8 to restore the ] we found.
    scan_fwd = (
        ">" + s(8) + l( # Move Next, Check ]
            a(8) + ">" + s(8) # Restore, Move Next, Check ]
        ) + a(8) # Restore the found ]
    )

    # scan_back: Search for [ (0x07).
    # Logic: Move Left. Sub 7. If 0, Stop. Else Add 7, Repeat.
    scan_back = (
        "<" + s(7) + l( # Move Prev, Check [
            a(7) + "<" + s(7) # Restore, Move Prev, Check [
        ) + a(7) # Restore the found [
    )

    # --- DECODE ---
    # Opcode checks 1..8
    
    # 0x01 (>)
    act_1 = ">" + l( to_data + ">" + to_code + clr() ) + "<"
    # 0x02 (<)
    act_2 = ">" + l( to_data + "<" + to_code + clr() ) + "<"
    # 0x03 (+)
    act_3 = ">" + l( to_data + a(1) + to_code + clr() ) + "<"
    # 0x04 (-)
    act_4 = ">" + l( to_data + s(1) + to_code + clr() ) + "<"
    # 0x05 (.)
    act_5 = ">" + l( to_data + "." + to_code + clr() ) + "<"
    # 0x06 (,)
    act_6 = ">" + l( to_data + "," + to_code + clr() ) + "<"
    
    # 0x07 ([)
    # If Data==0, Scan Fwd. Else Enter (do nothing).
    act_7 = ">" + l(
        to_data + l( # Data != 0
             to_code + clr() # Exit Action (Clear Flag)
        )
        + a(1) + l( # Data == 0 (Flag is 1)
             to_code + scan_fwd # Go back to code and Scan!
             + clr() # Clear Flag
        )
        + clr()
    ) + "<"

    # 0x08 (])
    # If Data!=0, Scan Back. Else Exit (do nothing).
    act_8 = ">" + l(
        to_data + l( # Data != 0
             to_code + scan_back # Go back to code and Scan!
             + m(1) + clr() + m(-1) # Hack: Clear Flag (Temp is at m(1) relative to code?)
             # Wait, to_code brings us to [Op]. Temp is >. Flag is >>.
             # We need to clear Flag (Temp).
        )
        + to_code + clr() # Clear Flag (Data==0 case or after scan)
    ) + "<"
    # Note: to_data/to_code macros align us to [Op]. 
    # The 'l' loop surrounds the Flag check. 'clr()' clears the Flag/Temp.

    # Build Tree
    bf += s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( 
        clr() 
    ) + act_8 ) + act_7 ) + act_6 ) + act_5 ) + act_4 ) + act_3 ) + act_2 ) + act_1
    
    # Move to Next Instruction
    bf += ">]"

    # Convert
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    res = "".join([mapping[c] for c in bf if c in mapping])
    print(res, end='')

if __name__ == "__main__":
    main()
