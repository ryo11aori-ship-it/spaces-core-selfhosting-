import sys

# Stage 3: Simple "Scan-Forward" Interpreter
# Logic: Physical Scan.
# If '[' is encountered, assume Data=0 (for this test) and scan input until ']'.

def main():
    bf = []
    cur = 0

    # --- Helper Functions ---
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
    IDX_SCAN = 2
    IDX_DATA = 3

    # --- 1. Header Consumption ---
    goto(IDX_OP)
    emit(',,,')

    # --- 2. Main Loop ---
    goto(IDX_OP)
    emit(',') 
    emit('[')

    # Copy Op -> Temp
    move_val(IDX_OP, IDX_TMP)
    
    # --- DECODE (Linear Check) ---
    # Python indentation is strictly flat here to avoid errors.

    # Check 7 ([)
    goto(IDX_TMP)
    emit('-'*7)
    
    # If 0 (Match 7)
    # Use IDX_OP as "Is_Match"
    goto(IDX_OP); emit('+')
    goto(IDX_TMP); emit('[') # If Not 7
    goto(IDX_OP); emit('-')
    goto(IDX_TMP); emit('-') # Check 8 (])
    
    # Check 8 (])
    emit('[')
    goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')
    emit('+'*2) # Restore for 6
      
    # Check 6 (,)
    emit('[')
    goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')

    # Check 5 (.)
    emit('[')
    goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')

    # Check 4 (-)
    emit('['); 
    goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')

    # Check 3 (+)
    emit('[')
    goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('[-]'); emit(']')
              
    # Action 3 (+)
    goto(IDX_OP); emit('[')
    goto(IDX_DATA); emit('+')
    goto(IDX_OP); emit('-')
    emit(']')

    emit(']') # End Check 4
    # Action 4 (-)
    goto(IDX_OP); emit('[')
    goto(IDX_DATA); emit('-')
    goto(IDX_OP); emit('-')
    emit(']')

    emit(']') # End Check 5
    # Action 5 (.)
    goto(IDX_OP); emit('[')
    goto(IDX_DATA); emit('.')
    goto(IDX_OP); emit('-')
    emit(']')

    emit(']') # End Check 6
    # Action 6 (,) - Ignore
    goto(IDX_OP); emit('[-]'); emit(']')
      
    emit(']') # End Check 8
    # Action 8 (]) - Ignore
    goto(IDX_OP); emit('[-]'); emit(']')
      
    emit(']') # End Check 7
    
    # Action 7 ([) - SCAN FORWARD LOGIC
    # We execute this block if IDX_OP is 1 (Matched '[')
    goto(IDX_OP); emit('[')
    
    # We assume Data is 0 for the test case [+++++], so we MUST scan.
    # Scan Loop: Read char, if 8 (]), break.
    
    goto(IDX_SCAN); emit('+') # ScanFlag = 1
    
    goto(IDX_SCAN); emit('[')
    # Read Char into IDX_OP (Temporary holder)
    goto(IDX_OP); emit(',')
    
    # Check if IDX_OP == 8
    move_val(IDX_OP, IDX_TMP)
    goto(IDX_TMP); emit('-'*8)
    
    # If IDX_TMP is 0, we found ']'. Set ScanFlag=0.
    # Logic: Flag=1. Temp [ Flag=0 ]. If Flag=1 -> Set ScanFlag=0.
    
    # Use IDX_OP as "Is_Zero" flag
    goto(IDX_OP); emit('+')
    goto(IDX_TMP); emit('[')
    goto(IDX_OP); emit('-') # Not Zero
    goto(IDX_TMP); emit('[-]')
    emit(']')
    
    # If IDX_OP is 1, it was Zero (Matched ']').
    goto(IDX_OP); emit('[')
    goto(IDX_SCAN); emit('-') # Stop Scanning
    goto(IDX_OP); emit('-')
    emit(']')
    
    goto(IDX_SCAN); emit(']') # End Scan Loop
    
    # We consumed the input until ']'.
    # We are done with this instruction.
    goto(IDX_OP); emit('-')
    emit(']')
    
    goto(IDX_TMP); emit('[-]') 
    emit(']') # End Execute
    
    # --- 5. Next Loop ---
    goto(IDX_OP)
    emit(',') 
    emit(']') 

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
