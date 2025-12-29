import sys

def main():
    # Helper functions
    def m(n): return ">"*n if n>0 else "<"*abs(n)
    def a(n): return "+"*n
    def s(n): return "-"*n
    def l(c): return "[" + c + "]"
    def clr(): return "[-]"

    # --- Full Interpreter Logic ---
    # Memory Layout: [Code...] 0 [Data...]
    # Start: Code is loaded, pointer at the end of Code.
    
    bf = ""
    # 1. Skip Header (S, P, A)
    bf += ">" + ","*3 
    
    # 2. Read Code (until 0)
    bf += ">>>+[,[>]+<[-]<]>>"
    
    # 3. Execution Loop
    # Go to start of Code
    bf += "[[>]+<[-]<]>"
    
    # Copy Opcode to check
    bf += "[[>+>+<<-]>>[<<+>>-]<" 
    
    # --- DECODE NEST ---
    # Structure: s + l( next_check + action )
    # If match, loop skipped, action executed.
    # 8 opcodes to check: 0x01..0x08
    
    # 0x01 (>)
    bf += "s" + l(
        # 0x02 (<)
        "s" + l(
            # 0x03 (+)
            "s" + l(
                # 0x04 (-)
                "s" + l(
                    # 0x05 (.)
                    "s" + l(
                        # 0x06 (,)
                        "s" + l(
                            # 0x07 ([)
                            "s" + l(
                                # 0x08 (])
                                "s" + l(
                                    # Unknown Op (Clear and exit)
                                    clr()
                                )
                                # Action 0x08 (])
                                + "m<[<]>[>]>m"
                            )
                            # Action 0x07 ([)
                            + "m<[<]>+>[>]>m"
                        )
                        # Action 0x06 (,)
                        + "m,m"
                    )
                    # Action 0x05 (.)
                    + "m.m"
                )
                # Action 0x04 (-)
                + "msm"
            )
            # Action 0x03 (+)
            + "mam"
        )
        # Action 0x02 (<)
        + "<"
    )
    # Action 0x01 (>)
    + ">"
    
    # Next Instruction
    + ">>]"

    # Replace macros to standard BF
    # m: Move to Data (from Code)
    # logic: [<] moves to start of code (0), > moves to Data separator (0), [>] moves to end of Data, > moves to new Data cell? 
    # Actually the macro 'm' used in DBFI is specific: "[<]>[>]>"
    # It assumes layout: 0 [Code] 0 [Data] 0
    # From Code cell: [<] goes to left 0. > goes to Code start. [>] goes to right 0. > goes to Data start.
    final_bf = bf.replace("m", "[<]>[>]>").replace("a","+").replace("s","-").replace("l","[")
    
    # Convert to Spaces
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    res = "".join([mapping[c] for c in final_bf if c in mapping])
    print(res, end='')

if __name__ == "__main__":
    main()
