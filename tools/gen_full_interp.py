import sys

# Stage 3: Robust Linear-Check Interpreter with Safe Scan
# Features:
# - Linear If-Chain for decoding (1..8) to avoid nesting hell.
# - Safety break on EOF (0) in Scan loop.
# - Flattened indentation to prevent Python syntax errors.

def main():
    bf = []
    cur = 0

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

    def copy_val(src, dst, tmp):
        clear(dst)
        clear(tmp)
        goto(src)
        emit('[')
        emit('-')
        goto(dst); emit('+')
        goto(tmp); emit('+')
        goto(src)
        emit(']')
        move_val(tmp, src)

    IDX_OP   = 0
    IDX_TMP  = 1 
    IDX_FLAG = 2 
    IDX_DATA = 3
    IDX_EXTRA = 4
    IDX_EXTRA_2 = 5
    IDX_IS_MATCH = 6
    IDX_SCAN_FLAG = 7
    IDX_CHAR = 8

    # --- 1. Header Consumption ---
    goto(IDX_OP); emit(',,,')

    # --- 2. Main Loop ---
    goto(IDX_OP); emit(',')
    emit('[')

    # Copy Op to Temp for decoding
    copy_val(IDX_OP, IDX_TMP, IDX_FLAG)
    
    # Initialize Done_Flag = 0
    clear(IDX_FLAG)

    # --- Helper to generate check block ---
    def check_opcode_and_act(action_func):
        # Check if Done_Flag (IDX_FLAG) == 0
        # Invert Flag into IDX_EXTRA: 1 if Not Done, 0 if Done
        clear(IDX_EXTRA); emit('+')
        goto(IDX_FLAG); emit('['); goto(IDX_EXTRA); emit('-'); goto(IDX_FLAG); emit('[-]+'); emit(']')
        
        goto(IDX_EXTRA)
        emit('[')
        # { Not Done Yet }
            
            # Move Temp (Current Op Value) -> IDX_EXTRA_2
            move_val(IDX_TMP, IDX_EXTRA_2)
            
            # Decrement Extra2 (The check)
            goto(IDX_EXTRA_2); emit('-')
            
            # Check if 0 (Match)
            # Set Match=1
            clear(IDX_IS_MATCH); emit('+')
            
            goto(IDX_EXTRA_2); emit('[')
                 # Not Zero
                 goto(IDX_IS_MATCH); emit('-') # Match=0
                 emit('-') # Decrement for next pass
                 goto(IDX_TMP); emit('+') # Restore remaining to Temp
                 goto(IDX_EXTRA_2)
            emit(']')
            
            goto(IDX_IS_MATCH)
            emit('[')
                 # MATCHED!
                 action_func()
                 goto(IDX_FLAG); emit('+') # Set Done_Flag=1
                 goto(IDX_IS_MATCH); emit('-')
            emit(']')
        
        clear(IDX_EXTRA) # Exit Not Done block
        emit(']')

    # --- Define Actions ---
    def act_plus():
        goto(IDX_DATA); emit('+')

    def act_minus():
        goto(IDX_DATA); emit('-')

    def act_dot():
        goto(IDX_DATA); emit('.')
        
    def act_scan():
        # Scan until ] (8) or 0 (EOF)
        # Set ScanFlag = 1
        clear(IDX_SCAN_FLAG); emit('+')
        
        goto(IDX_SCAN_FLAG)
        emit('[')
             # Read char -> IDX_CHAR
             goto(IDX_CHAR); emit(',')
             
             # Check if 0 (EOF) - Safety Break
             copy_val(IDX_CHAR, IDX_EXTRA, IDX_EXTRA_2)
             
             # Invert into Match (1 if 0, 0 if !0)
             clear(IDX_IS_MATCH); emit('+')
             goto(IDX_EXTRA); emit('['); goto(IDX_IS_MATCH); emit('-'); goto(IDX_EXTRA); emit('[-]'); emit(']')
             
             goto(IDX_IS_MATCH); emit('[')
                  # Is EOF (0). Clear ScanFlag to Stop.
                  clear(IDX_SCAN_FLAG)
                  clear(IDX_IS_MATCH)
             emit(']')
             
             # If Still Scanning, Check if 8 (])
             copy_val(IDX_SCAN_FLAG, IDX_EXTRA, IDX_EXTRA_2) # Copy Flag
             goto(IDX_EXTRA); emit('[')
                  # Check 8
                  copy_val(IDX_CHAR, IDX_EXTRA_2, IDX_EXTRA)
                  goto(IDX_EXTRA_2); emit('-'*8)
                  
                  # Check if 0
                  clear(IDX_IS_MATCH); emit('+')
                  goto(IDX_EXTRA_2); emit('['); goto(IDX_IS_MATCH); emit('-'); goto(IDX_EXTRA_2); emit('[-]'); emit(']')
                  
                  goto(IDX_IS_MATCH); emit('[')
                       # Is 8 (]). Clear ScanFlag.
                       clear(IDX_SCAN_FLAG)
                       clear(IDX_IS_MATCH)
                  emit(']')
                  
                  clear(IDX_EXTRA)
             emit(']')
             
        goto(IDX_SCAN_FLAG); emit(']') # Loop

    # --- Generate Checks 1..8 ---
    check_opcode_and_act(lambda: None) # 1
    check_opcode_and_act(lambda: None) # 2
    check_opcode_and_act(act_plus)     # 3 (+)
    check_opcode_and_act(act_minus)    # 4 (-)
    check_opcode_and_act(act_dot)      # 5 (.)
    check_opcode_and_act(lambda: None) # 6
    check_opcode_and_act(act_scan)     # 7 ([) - Safe Scan
    check_opcode_and_act(lambda: None) # 8 (])
    
    # End Main Loop
    goto(IDX_OP); emit(']')

    # Output
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    print("".join([mapping.get(c, '') for c in bf]), end='')

if __name__ == "__main__":
    main()
