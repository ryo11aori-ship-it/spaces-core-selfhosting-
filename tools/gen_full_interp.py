import sys

def main():
    # Helper functions
    def m(n): return ">"*n if n>0 else "<"*abs(n)
    def a(n): return "+"*n
    def s(n): return "-"*n
    def l(c): return "[" + c + "]"
    def clr(): return "[-]"

    # --- Fixed-Cell Interpreter Logic ---
    # Memory Layout: [Code...] 0 [Temp] [Flag] 0 [Data(SingleCell)]
    
    # Macros for fixed movement (No dynamic pointer shifts!)
    # We always assume Data is at fixed distance from Code end.
    to_data = "[>]>>" 
    to_code = "<<[<]" 

    bf = ""
    # 1. Skip Header
    bf += m(1) + ","*3 
    
    # 2. Read Code (until 0)
    bf += m(3) + a(1) + l( "," + l( m(1) ) + a(1) + m(-1) + s(1) + m(-1) ) + m(2)
    
    # 3. Go to Code Start
    bf += "<[<]>"
    
    # 4. Main Loop
    bf += "["
    
    # Copy Opcode to Temp
    bf += l( m(1)+a(1)+m(1)+a(1)+m(-2) ) + m(2) + l(m(-2)+a(1)+m(2)) + m(-2)
    
    # --- SCAN LOGIC (Robust) ---
    # Scan Forward (Find matching ])
    scan_fwd = (
        ">" + s(8) + l( a(8) + ">" + s(8) ) + a(8)
    )
    # Scan Backward (Find matching [)
    scan_back = (
        "<" + s(7) + l( a(7) + "<" + s(7) ) + a(7)
    )

    # --- DECODE ---
    # 0x01 (>) : No-Op (Disabled for safety)
    act_1 = ">" + l( clr() ) + "<"
    # 0x02 (<) : No-Op
    act_2 = ">" + l( clr() ) + "<"
    
    # 0x03 (+)
    act_3 = ">" + l( to_data + a(1) + to_code + clr() ) + "<"
    # 0x04 (-)
    act_4 = ">" + l( to_data + s(1) + to_code + clr() ) + "<"
    # 0x05 (.)
    act_5 = ">" + l( to_data + "." + to_code + clr() ) + "<"
    # 0x06 (,)
    act_6 = ">" + l( to_data + "," + to_code + clr() ) + "<"
    
    # 0x07 ([) : If Data==0, Scan Fwd.
    act_7 = ">" + l(
        to_data + l( to_code + clr() ) # Data!=0 -> Enter
        + a(1) + l( to_code + scan_fwd + clr() ) # Data==0 -> Skip
        + clr()
    ) + "<"

    # 0x08 (]) : If Data!=0, Scan Back.
    act_8 = ">" + l(
        to_data + l( 
            to_code + scan_back 
            + m(1) + clr() + m(-1) # Hack: Fix Flag state after scan
        )
        + to_code + clr()
    ) + "<"

    # Build Decode Tree
    bf += s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( ">a<" + s(1) + l( 
        clr() 
    ) + act_8 ) + act_7 ) + act_6 ) + act_5 ) + act_4 ) + act_3 ) + act_2 ) + act_1
    
    # Next Instruction
    bf += ">]"

    # Convert to Spaces
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    res = "".join([mapping[c] for c in bf if c in mapping])
    print(res, end='')

if __name__ == "__main__":
    main()
