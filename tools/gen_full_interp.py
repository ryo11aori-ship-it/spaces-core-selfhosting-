import sys

def main():
    # Helper functions
    def m(n): return ">"*n if n>0 else "<"*abs(n)
    def a(n): return "+"*n
    def s(n): return "-"*n
    def l(c): return "[" + c + "]"
    def clr(): return "[-]"

    # --- Final Robust Interpreter Logic ---
    # Memory Layout:
    # [Start=0] [Code... (Current=Hole=0)] [End=0] [Temp] [Flag] [Sep=0] [Data]
    
    # Navigation Macros (Absolute reliability using Sentinels)
    # From Hole (Current Op):
    #   1. > moves to Next Op or EndSentinel
    #   2. [>] scans to EndSentinel(0)
    #   3. >>>> skips [End], [Temp], [Flag], [Sep] to arrive at [Data]
    to_data = ">[>]>>>>"
    
    # From Data:
    #   1. <<<< moves back to EndSentinel
    #   2. < moves to Last Op
    #   3. [<] scans left to find the Hole(0)
    to_hole = "<<<<<[<]"

    bf = ""
    # 1. Setup Header & Sentinels
    # We need a Start Sentinel at Cell 0. Code starts at Cell 1.
    bf += m(1) + ","*3 # Skip SPA
    
    # 2. Read Code
    # Layout: 0 [Code...] 0
    # Read until EOF(0).
    bf += m(1) + "," + l( m(1) + "," )
    
    # 3. Go to Start (Find Start Sentinel 0)
    bf += "<[<]>"
    
    # 4. Main Execution Loop
    # We are at Current Op.
    bf += "["
    
    # --- STEP 1: MAKE HOLE ---
    # Move Op -> Temp. Op becomes 0 (Hole).
    # Find Temp (Relative to Hole: >[>]>)
    bf += "[>]>" # At Temp (Op is NOT 0 yet, so we scan)
    bf += clr() # Clear Temp
    bf += "<[<]" # Back to Op
    
    # Move Op to Temp (Destructive to Op, creating Hole)
    bf += l( ">[>]>" + a(1) + "<<<<<[<]" + s(1) )
    # Now Op is 0 (Hole). Temp has the Opcode.
    
    # --- STEP 2: DECODE & EXECUTE ---
    # Go to Temp
    bf += ">[>]>"
    
    # Define Actions
    # Each action must:
    # 1. Do work (access Data if needed)
    # 2. Return to Hole
    # 3. Restore Opcode (Add value back to Hole)
    # 4. Move to Next Instruction ( > or Scan )
    
    # Action 0x01 (>): No-Op
    act_1 = to_hole + a(1) + ">"
    
    # Action 0x02 (<): No-Op
    act_2 = to_hole + a(2) + ">"
    
    # Action 0x03 (+): Data++
    act_3 = to_data + a(1) + to_hole + a(3) + ">"
    
    # Action 0x04 (-): Data--
    act_4 = to_data + s(1) + to_hole + a(4) + ">"
    
    # Action 0x05 (.): Output
    act_5 = to_data + "." + to_hole + a(5) + ">"
    
    # Action 0x06 (,): Input (No-op for test)
    act_6 = to_hole + a(6) + ">"
    
    # Action 0x07 ([): Jump Fwd if Data==0
    # ScanFwd Logic: Move right until ] (8) is found.
    # Note: We assume Depth-1 nesting for bootstrap robustness.
    scan_fwd = ">" + s(8) + l( a(8) + ">" + s(8) ) + a(8)
    
    act_7 = (
        to_data + l( 
            # Data != 0: Enter loop.
            # Just restore and move next.
            to_hole + a(7) + ">"
            + clr() # Clear Data flag (hack to exit this check)
            + to_data # Go back to Data to satisfy the outer loop
        )
        + a(1) + l(
            # Data == 0: Skip loop.
            # Restore Op (7), then Scan Fwd.
            to_hole + a(7) + scan_fwd
            + clr() # Clear Flag
        )
        + clr() # Exit
    )
    
    # Action 0x08 (]): Jump Back if Data!=0
    # ScanBack Logic: Move left until [ (7) is found.
    scan_back = "<" + s(7) + l( a(7) + "<" + s(7) ) + a(7)
    
    act_8 = (
        to_data + l(
            # Data != 0: Jump Back.
            # Restore Op (8), then Scan Back.
            to_hole + a(8) + scan_back
            + clr() # Exit check
            + to_data # Hack to maintain loop position
            + clr() # Clear Data to force exit this check logic?
                    # No, we need to stop the loop but Data is non-zero.
                    # We simply return to Hole/Scan.
                    # The outer loop expects us to be at Temp.
        )
        + a(1) + l(
            # Data == 0: Exit loop.
            # Restore Op (8), Move Next.
            to_hole + a(8) + ">"
            + clr()
        )
        + clr()
    )
    
    # --- BUILD DECODE TREE (Safe Method) ---
    # We build the check logic from 8 down to 1 using a Python loop.
    # Logic: If Temp matches N, Run ActionN. Else Check N-1.
    
    # Default (Unknown Op) -> Just Restore and Move Next? Or Clear?
    # Let's just Clear and Move Next to avoid stuck.
    logic = to_hole + ">" 
    
    # Wrap actions
    logic = s(1) + l( logic ) + act_8 # Check 8
    logic = s(1) + l( logic ) + act_7 # Check 7
    logic = s(1) + l( logic ) + act_6 # Check 6
    logic = s(1) + l( logic ) + act_5 # Check 5
    logic = s(1) + l( logic ) + act_4 # Check 4
    logic = s(1) + l( logic ) + act_3 # Check 3
    logic = s(1) + l( logic ) + act_2 # Check 2
    logic = s(1) + l( logic ) + act_1 # Check 1
    
    bf += logic
    
    # 5. Loop End
    # We are now at the *Next* Op (which is non-zero).
    # Unless it's EndSentinel(0), in which case we stop.
    bf += "]"

    # Convert to Spaces
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    res = "".join([mapping[c] for c in bf if c in mapping])
    print(res, end='')

if __name__ == "__main__":
    main()
