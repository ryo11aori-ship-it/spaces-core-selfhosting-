import sys

# Stage 3: Deterministic "Skip-Logic" Interpreter generator
# Based on the user's robust pointer movement logic.
#
# Memory Layout:
# [0: Opcode] [1: Temp] [2: SkipFlag] [3: Data]

def main():
    bf = []
    cur = 0

    # --- Helper Functions (Deterministic Navigation) ---
    def emit(s):
        nonlocal cur
        bf.append(s)
        moves = [c for c in s if c in '<>']
        if moves:
            cur += moves.count('>') - moves.count('<')

    def goto(idx):
        nonlocal cur
        if idx > cur:
            emit('>' * (idx - cur))
        elif idx < cur:
            emit('<' * (cur - idx))
        cur = idx

    def clear(idx):
        goto(idx)
        emit('[-]')

    def move_val(src, dst):
        # Move value form src to dst (destructively)
        clear(dst)
        goto(src)
        emit('[')
        emit('-')
        goto(dst)
        emit('+')
        goto(src)
        emit(']')

    # --- Constants ---
    IDX_OP   = 0
    IDX_TMP  = 1
    IDX_SKIP = 2
    IDX_DATA = 3

    # --- 1. Header Consumption ---
    goto(IDX_OP)
    emit(',,,') # Skip SPA

    # --- 2. Main Loop Setup ---
    # Read first opcode
    goto(IDX_OP)
    emit(',') 
    
    # Loop while Opcode != 0
    emit('[')

    # Move Opcode -> Temp (to process it without losing track)
    move_val(IDX_OP, IDX_TMP)

    # --- 3. Check SkipFlag ---
    # Determine if we are Skipping or Executing based on IDX_SKIP.
    # Move SkipFlag -> IDX_OP to use as "Is_Skipping" flag
    move_val(IDX_SKIP, IDX_OP)
    
    # Now IDX_OP is 1 if skipping, 0 if executing.
    goto(IDX_OP)
    emit('[') 
    # === SKIPPING MODE (Inside Loop: Op=1) ===
    # Check if IDX_TMP == 8 (])
    goto(IDX_TMP)
    emit('-'*8)
    
    # Check if Temp is 0 (Match found)
    # Use IDX_SKIP as "Found" flag (currently 0)
    goto(IDX_SKIP)
    emit('+') # Found=1
    
    goto(IDX_TMP)
    emit('[') # If Temp!=0 (Not ']')
    goto(IDX_SKIP)
    emit('-') # Found=0
    goto(IDX_TMP)
    emit('[-]')
    emit(']')
    
    # Check Found (IDX_SKIP)
    goto(IDX_SKIP)
    emit('[') # If Found=1 (Found ']')
    goto(IDX_OP)
    emit('[-]') # Set Is_Skipping = 0 (Clear Loop Flag)
    goto(IDX_SKIP)
    emit('-') # Clear Found
    emit(']')
    
    # If Is_Skipping (Op) is still 1, we preserve it.
    # Move Op -> IDX_SKIP (Restore State)
    move_val(IDX_OP, IDX_SKIP) 
    
    goto(IDX_OP) # Should be 0
    emit(']') # End Skip Logic
    
    
    # --- 4. Execute Logic ---
    # We execute ONLY if IDX_SKIP == 0.
    # And if IDX_TMP != 0 (instruction exists and wasn't consumed by skip logic).
    
    goto(IDX_TMP)
    emit('[') 
    # === EXECUTE MODE (Temp has Opcode) ===
    
    # DECODE (Subtract approach)
    # Check 7 ([)
    emit('-'*7)
    
    # Try `[` (7)
    # We use IDX_OP as "Is_Match" flag.
    goto(IDX_OP); emit('+')
    goto(IDX_TMP); emit('[') # If not 0 (Not 7)
    goto(IDX_OP); emit('-')
    goto(IDX_TMP); emit('-') # Check 8 (])
    
    # Try `]` (8)
    emit('['); 
    goto(IDX_OP); emit('-'); 
    goto(IDX_TMP); emit('-') # If not 0 (Not 8)
    
    # Restore for checks 3,4,5,6
    # Original - 8. Add 2 -> Original - 6
    emit('+'*2)
    
    # Check 6 (,)
    emit('['); 
    goto(IDX_OP); emit('-'); 
    goto(IDX_TMP); emit('-')
    
    # Check 5 (.)
    emit('['); 
    goto(IDX_OP); emit('-'); 
    goto(IDX_TMP); emit('-')
    
    # Check 4 (-)
    emit('['); 
    goto(IDX_OP); emit('-'); 
    goto(IDX_TMP); emit('-')
    
    # Check 3 (+)
    emit('['); 
    goto(IDX_OP); emit('-'); 
    goto(IDX_TMP); emit('[-]') # Consume rest
    emit(']')
    
    # === ACTIONS ===
    # Here we are deep in nested brackets. 
    # But since we use IDX_OP as "Match Flag", we can just close all brackets
    # and check logic linearly below? No, we lost the state.
    
    # Correct linear approach:
    # Just close the nesting carefully.
    emit(']') # End Check 3
    
    # If Match (Op=1): Action 3 (+)
    goto(IDX_DATA); emit('+'); goto(IDX_OP)
    
    emit(']') # End Check 4
    # Action 4 (-)
    goto(IDX_DATA); emit('-'); goto(IDX_OP)
    
    emit(']') # End Check 5
    # Action 5 (.)
    goto(IDX_DATA); emit('.'); goto(IDX_OP)
    
    emit(']') # End Check 6
    # Action 6 (,) - Ignore
    
    emit(']') # End Check 8
    # Action 8 (]) - Ignore (End of loop iteration)
    
    emit(']') # End Check 7
    
    # Action 7 ([) logic
    # If Match (Op=1): Check Data. If 0, Set SkipFlag=1.
    # We are at IDX_TMP (0). IDX_OP is 1.
    
    # To run this only if Match=1:
    goto(IDX_OP)
    emit('[')
    # Action 7 Logic:
    goto(IDX_SKIP); emit('+') # Flag/Skip = 1
    goto(IDX_DATA); emit('[') # If Data!=0
    goto(IDX_SKIP); emit('-') # Skip = 0
    goto(IDX_DATA); emit('[') # Clear Data temporarily to exit check? No, restore.
    emit('-')
    goto(IDX_TMP); emit('+') # Backup
    goto(IDX_DATA); emit(']')
    # Restore Data
    goto(IDX_TMP); emit('['); emit('-'); goto(IDX_DATA); emit('+'); goto(IDX_TMP); emit(']')
    goto(IDX_DATA); emit(']')
    
    goto(IDX_OP); emit('-') # Clear Match Flag
    emit(']')
    
    # End of Decode Tree
    goto(IDX_TMP); emit('[-]') # Ensure Temp is clear
    emit(']') # End Execute Logic (If Temp!=0)
    
    # --- 5. Next Loop ---
    goto(IDX_OP)
    emit(',') # Read next opcode
    emit(']') # End Main Loop

    # --- Output ---
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    
    res = []
    for c in bf:
        if c in mapping:
            res.append(mapping[c])
    print("".join(res), end='')

if __name__ == "__main__":
    main()
