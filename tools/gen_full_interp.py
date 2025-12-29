import sys

def main():
    # Helper functions
    def m(n): return ">"*n if n>0 else "<"*abs(n)
    def a(n): return "+"*n
    def s(n): return "-"*n
    def l(c): return "[" + c + "]"
    def clr(): return "[-]"

    # --- Full Interpreter Logic ---
    # Memory Layout: 0 0 [StartMarker=1] [Code...] 0 [Temp/Op] [Flag] 0 [Data...]
    
    # Macro: Move Focus
    to_data = "[<]>[>]>"
    to_code = "<[<]>[>]<" 

    bf = ""
    # 1. Skip Header
    bf += m(1) + ","*3 
    
    # 2. Read Code (until 0)
    bf += m(3) + a(1) + l( "," + l( m(1) ) + a(1) + m(-1) + s(1) + m(-1) ) + m(2)
    
    # 3. Go to Code Start
    bf += l( l( m(1) ) + a(1) + m(-1) + s(1) + m(-1) ) + m(1)
    
    # 4. Main Loop
    bf += "["
    
    # Copy Opcode to Temp
    bf += l( m(1)+a(1)+m(1)+a(1)+m(-2) ) + m(2) + l(m(-2)+a(1)+m(2)) + m(-2)
    
    # --- Action Definitions (Defined separately to avoid SyntaxError) ---
    
    # Action 0x08 (]): Scan Backward if Data != 0
    # Scan logic: Counter starts at 1. Move Left. If ] inc, if [ dec. Stop at 0.
    # Note: 0x07=[, 0x08=]
    scan_back = (
        to_code + m(-1) + l(m(-1)) + m(-1) # Move Left past current op
        + l( # Scan Loop
             m(-1) + l(m(-1)) + m(1) # Move to Op
             + s(7) + l( # Not 0x07 ([)
                 s(1) + l( # Not 0x08 (])
                     a(8) # Restore
                     + clr()
                 )
                 + a(1) + l( # Is 0x08 (]) -> Nested
                     a(7) + m(1) + a(1) + m(-1) # Inc Counter
                     + clr()
                 )
                 + clr()
             )
             + a(1) + l( # Is 0x07 ([) -> Matching or Nested
                 a(7) + m(1) + s(1) + m(-1) # Dec Counter
                 + clr()
             )
             + a(7) + m(1) # Check Counter
        )
        + m(2) + clr() + m(1) # Clear Flag, Return to Data
    )
    act_8 = ">" + l( to_data + l( scan_back ) + to_code + clr() ) + "<"

    # Action 0x07 ([): Scan Forward if Data == 0
    # Scan logic: Counter starts at 1. Move Right. If [ inc, if ] dec. Stop at 0.
    scan_fwd = (
        to_code + m(1) + l(m(1)) + m(1) # Move Right past current op
        + l( # Scan Loop
             m(1) + l(m(1)) + m(-1) # Move to Op
             + s(7) + l( # Not 0x07 ([)
                 s(1) + l( # Not 0x08 (])
                     a(8) + clr()
                 )
                 + a(1) + l( # Is 0x08 (]) -> Matching or Nested
                     a(7) + m(-1) + s(1) + m(1) # Dec Counter
                     + clr()
                 )
                 + clr()
             )
             + a(1) + l( # Is 0x07 ([) -> Nested
                 a(7) + m(-1) + a(1) + m(1) # Inc Counter
                 + clr()
             )
             + a(7) + m(-1) # Check Counter
        )
        + m(2) + clr() # Clear Flag
    )
    act_7 = ">" + l( 
        to_data + l( to_code + clr() ) # Data!=0, Enter loop (Clear Flag)
        + a(1) + l( # Data==0, Scan Forward
             scan_fwd
        ) + clr()
    ) + "<"

    act_6 = ">" + l( to_data + "," + to_code + clr() ) + "<"
    act_5 = ">" + l( to_data + "." + to_code + clr() ) + "<"
    act_4 = ">" + l( to_data + s(1) + to_code + clr() ) + "<"
    act_3 = ">" + l( to_data + a(1) + to_code + clr() ) + "<"
    act_2 = ">" + l( to_data + "<" + to_code + clr() ) + "<"
    act_1 = ">" + l( to_data + ">" + to_code + clr() ) + "<"

    # --- Build Decode Tree ---
    bf += s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( 
        clr() 
    ) + act_8 ) + act_7 ) + act_6 ) + act_5 ) + act_4 ) + act_3 ) + act_2 ) + act_1
    
    # Next Instruction
    bf += ">>]"

    # Convert to Spaces
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    res = "".join([mapping[c] for c in bf if c in mapping])
    print(res, end='')

if __name__ == "__main__":
    main()
