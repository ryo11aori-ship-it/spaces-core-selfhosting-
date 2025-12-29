import sys

def main():
    # Helper functions
    def m(n): return ">"*n if n>0 else "<"*abs(n)
    def a(n): return "+"*n
    def s(n): return "-"*n
    def l(c): return "[" + c + "]"
    def clr(): return "[-]"

    # --- Hole-Marking Interpreter Logic ---
    # Memory Layout:
    # [StartSentinel=0] [Code... (Current=0)] [EndSentinel=0] [Temp] [Flag] [Sep=0] [Data]
    
    # Macros for absolute navigation
    # From Hole (Current Op which is 0):
    #   1. `>` moves to next Op (or EndSentinel)
    #   2. `[>]` skips remaining code to EndSentinel
    #   3. `>>>` skips [Temp], [Flag], [Sep] to arrive at [Data]
    to_data = ">[>]>>>"
    
    # From Data:
    #   1. `<<<` moves back to EndSentinel
    #   2. `<` moves to last Op
    #   3. `[<]` scans left until StartSentinel (0)
    #   4. `>` moves to first Op
    #   5. `[>]` scans right until it hits the Hole (0)
    return_to_hole = "<<<<[<]>[>]"

    bf = ""
    # 1. Skip Header (S, P, A)
    bf += m(1) + ","*3 
    
    # 2. Read Code
    # Setup StartSentinel(0) at Cell 0. Code starts at Cell 1.
    # We read until EOF (0).
    bf += m(1) + "," + l( m(1) + "," )
    
    # 3. Execution Loop
    # Go to Code Start
    bf += "<[<]>"
    
    # Main Loop (Iterate while Op exists)
    bf += "["
    
    # --- STEP 1: MAKE HOLE ---
    # Copy Current Op to Temp, then set Current Op to 0 (Hole).
    # Layout: [Op] [EndSentinel] [Temp]
    # We need to move Op to Temp.
    # Find EndSentinel first.
    bf += "[>]>" # At Temp
    bf += clr() # Clear Temp
    bf += "<[<]>[>]" # Back to Op (Hole logic won't work yet as Op is not 0, so we use scan)
    # Actually, simpler copy:
    bf += s(1) + l( # Dec Op
        ">[>]> a(1) " + return_to_hole + s(1) # Inc Temp, Return, Dec Op
    )
    # Now Op is 0 (Hole Created). Temp holds the value.
    
    # --- STEP 2: DECODE TEMP ---
    # Go to Temp
    bf += ">[>]>"
    
    # Decode logic (Standard 1..8)
    # 0x01 (>) : No-Op
    act_1 = clr()
    # 0x02 (<) : No-Op
    act_2 = clr()
    
    # 0x03 (+)
    act_3 = ">" + a(1) + "<" + clr()
    # 0x04 (-)
    act_4 = ">" + s(1) + "<" + clr()
    # 0x05 (.)
    act_5 = ">.<" + clr()
    # 0x06 (,)
    act_6 = clr() # No input for this test
    
    # 0x07 ([)
    # Logic: Check Data (>). If 0, Restore Op, Scan Fwd, Update Hole.
    # Note: We are at Temp. Data is at >.
    act_7 = (
        ">" + l( # Data != 0
            "<" + clr() + ">" # Clear Temp (Exit), stay at Data
        )
        + "<" + a(1) + l( # Data == 0 (Temp is still 7)
            # Restore Op (The Hole) to 7
            return_to_hole + a(7)
            # Scan Fwd for matching ]
            + ">" + s(8) + l( a(8) + ">" + s(8) ) + a(8)
            # We found ]. Now make THIS the new Hole (0).
            # But wait, the main loop expects Temp to be populated? 
            # No, main loop expects us to return to a Hole.
            # We set current ] to 0.
            + "[-]" 
            # Go to Temp and Clear it (loop exit)
            + ">[>]>" + clr()
        )
        + clr() # Exit
    )

    # 0x08 (])
    # Logic: Check Data. If != 0, Restore Op, Scan Back.
    act_8 = (
        ">" + l( # Data != 0
            # Restore Op to 8
            "<" + return_to_hole + a(8)
            # Scan Back for matching [
            + "<" + s(7) + l( a(7) + "<" + s(7) ) + a(7)
            # Found [. Make it Hole.
            + "[-]"
            # Go to Temp and Clear (loop exit)
            + ">[>]>" + clr()
            # Fix Data pointer for the loop check
            + "> a(1) <" 
        )
        + "<" + clr() # Exit if Data == 0
    )

    # Build Decode Tree on Temp
    bf += s(1) + l( s(1) + l( s(1) + l( s(1) + l( s(1) + l( s(1) + l( s(1) + l( 
        clr() 
    ) + act_8 ) + act_7 ) + act_6 ) + act_5 ) + act_4 ) + act_3 ) + act_2 ) + act_1
    
    # --- STEP 3: RESTORE & NEXT ---
    # If we didn't jump (Temp is 0), we must return to Hole and Restore it from a Backup?
    # Wait, the decode destroyed Temp.
    # We need to restore the Opcode into the Hole *unless* we jumped.
    # But we don't know what the Opcode was!
    
    # Correction: The Decode Tree destroys Temp.
    # We should have preserved it?
    # No, simpler: The Main Loop iterates.
    # If we are at Hole (0), we move Right.
    # But we need the value back to know if it wasn't 0 (EOF).
    
    # REVISED STRATEGY for Restore:
    # We don't restore. We leave the old instruction as 0 (Hole)?
    # No, code must be reusable for loops.
    # We must restore.
    
    # Let's use Flag to hold a copy of Op.
    # Layout: [Op] ... [Temp] [Flag]
    # Copy Op -> Temp AND Flag.
    # Decode Temp.
    # After Decode, move Flag -> Op (Restore).
    
    # IMPLEMENTATION:
    # 1. At Op (Start of loop). Move to Temp.
    #    Op -> Temp, Op -> Flag. Op becomes 0.
    
    # Go back to Op (it is non-zero now).
    return_to_hole_simple = "<<<<[<]>[>]"
    
    # Go to Temp/Flag
    bf += return_to_hole + ">[>]>" # At Temp
    
    # Restore Logic (Move Flag -> Op)
    # Temp is 0 (consumed). Flag has copy.
    bf += ">" + l( 
        "<" + return_to_hole + a(1) # Add to Op
        + ">[>]>>" + s(1) # Back to Flag, Dec
    )
    
    # Move to Next Op
    # At Flag (0).
    bf += "<" + return_to_hole + ">"
    
    # Loop repeats
    bf += "]"

    # Convert to Spaces
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    res = "".join([mapping[c] for c in bf if c in mapping])
    print(res, end='')

if __name__ == "__main__":
    main()
