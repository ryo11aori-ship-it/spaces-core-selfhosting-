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
    
    bf = ""
    # 1. Skip Header (S, P, A)
    bf += m(1) + ","*3 
    
    # 2. Read Code (until 0)
    # Init: 0 0 1 ...
    bf += m(3) + a(1) + l( "," + l( m(1) ) + a(1) + m(-1) + s(1) + m(-1) ) + m(2)
    
    # 3. Execution Loop
    # Go to start of Code (Find Marker 1)
    bf += l( l( m(1) ) + a(1) + m(-1) + s(1) + m(-1) ) + m(1)
    
    # Copy Opcode to Temp
    bf += l( l( m(1) + a(1) + m(1) + a(1) + m(-2) ) + m(2) + l( m(-2) + a(1) + m(2) ) + m(-1) + s(1) ) + m(-1)
    
    # --- DECODE NEST (Flag Method) ---
    # Structure:
    # Op - 1
    # [ Flag=1, Op-1 [ ... ] Flag_Check [ Action ] ]
    # Flag_Check [ Action ]
    
    # Macros for movement between Code and Data
    # From Temp: [<] goes to Marker(1). > goes to Code Start. [>] goes to End(0). > goes to Data.
    to_data = "[<]>[>]>"
    to_code = "<[<]>[>]<" 

    # We use explicit parentheses to avoid TypeError
    bf += (
        # 0x01 (>)
        s(1) + l(
            ">a<" + # Set Flag=1
            # 0x02 (<)
            s(1) + l(
                ">a<" + # Set Flag=1
                # 0x03 (+)
                s(1) + l(
                    ">a<" + 
                    # 0x04 (-)
                    s(1) + l(
                        ">a<" +
                        # 0x05 (.)
                        s(1) + l(
                            ">a<" +
                            # 0x06 (,)
                            s(1) + l(
                                ">a<" +
                                # 0x07 ([)
                                s(1) + l(
                                    ">a<" +
                                    # 0x08 (])
                                    s(1) + l(
                                        clr() # Unknown Op
                                    )
                                    # Action 0x08 (])
                                    + ">" + l(
                                        to_data + l( # If Data!=0
                                            to_code + m(-1) + l(m(-1)) + m(-1) # Move Left
                                            + l( m(-1) + l(m(-1)) + m(1) ) # Scan back logic (simplified)
                                        ) + to_code 
                                        + clr() # Clear Flag
                                    ) + "<"
                                )
                                # Action 0x07 ([)
                                + ">" + l(
                                    to_data + l(
                                       to_code # Data!=0, Continue
                                       + clr() # Clear Flag (Exit Action)
                                    ) 
                                    + a(1) # Set Flag=1 if Data==0 to trigger Scan
                                    + l(
                                        to_code + m(1) + l(m(1)) + m(1) # Move Right
                                        + l( m(1) + l(m(1)) + m(-1) ) # Scan fwd logic (simplified)
                                        + clr()
                                    )
                                    + clr() # Clear Flag
                                ) + "<"
                            )
                            # Action 0x06 (,)
                            + ">" + l( to_data + "," + to_code + clr() ) + "<"
                        )
                        # Action 0x05 (.)
                        + ">" + l( to_data + "." + to_code + clr() ) + "<"
                    )
                    # Action 0x04 (-)
                    + ">" + l( to_data + s(1) + to_code + clr() ) + "<"
                )
                # Action 0x03 (+)
                + ">" + l( to_data + a(1) + to_code + clr() ) + "<"
            )
            # Action 0x02 (<)
            + ">" + l( to_data + "<" + to_code + clr() ) + "<"
        )
        # Action 0x01 (>)
        + ">" + l( to_data + ">" + to_code + clr() ) + "<"
        
        # Next Instruction
        + ">>]"
    )

    # Convert to Spaces
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    res = "".join([mapping[c] for c in bf if c in mapping])
    print(res, end='')

if __name__ == "__main__":
    main()
