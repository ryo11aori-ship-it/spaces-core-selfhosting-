import sys

# Stage 3: Robust Interpreter with "Linear Consumption" Scan
# Features:
# - Strictly flat indentation.
# - Scan Logic consumes input explicitly inside Action 7.
# 
# NOTE (fix): avoid reusing Done_Flag slot as temporary copy buffer.
# The original bug used IDX_FLAG as tmp in copy_val() and then cleared/used it as Done_Flag,
# causing the decode pipeline to be corrupted. We add a dedicated copy temp IDX_COPY_TMP.

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
        # move value from src -> dst (destructive on src)
        clear(dst)
        goto(src)
        emit('[')
        emit('-')
        goto(dst)
        emit('+')
        goto(src)
        emit(']')

    def copy_val(src, dst, tmp):
        # copy value src -> dst, using tmp as scratch, and restore src
        clear(dst)
        clear(tmp)
        goto(src)
        emit('[')
        emit('-')
        goto(dst); emit('+')
        goto(tmp); emit('+')
        goto(src)
        emit(']')
        # restore original src from tmp
        move_val(tmp, src)

    # Index map (cells)
    IDX_OP = 0
    IDX_TMP = 1 
    IDX_FLAG = 2 
    IDX_DATA = 3
    IDX_EXTRA = 4
    IDX_EXTRA_2 = 5
    IDX_IS_MATCH = 6
    IDX_SCAN_FLAG = 7
    IDX_CHAR = 8
    IDX_COPY_TMP = 9   # <-- NEW: dedicated temporary for copy_val to avoid overwriting IDX_FLAG

    # --- 1. Header Consumption ---
    goto(IDX_OP); emit(',,,')

    # --- 2. Main Loop ---
    goto(IDX_OP); emit(',')
    emit('[')

    # Copy Op to Temp  (use dedicated copy tmp so Done_Flag isn't reused)
    copy_val(IDX_OP, IDX_TMP, IDX_COPY_TMP)
    
    # Initialize Done_Flag = 0
    clear(IDX_FLAG)

    # --- Helper to generate check block ---
    def check_opcode_and_act(action_func):
        # Check if Done_Flag (IDX_FLAG) == 0
        # The sequence below implements:
        # if Done_Flag == 0: run the check; else skip
        clear(IDX_EXTRA); emit('+')
        goto(IDX_FLAG); emit('[')        # if flag != 0
        goto(IDX_EXTRA); emit('-')      # decrement marker to reflect flag set
        goto(IDX_FLAG); emit('[-]+')    # clear flag and set it to 1 (net effect is to consume the branch)
        emit(']')
        
        goto(IDX_EXTRA)
        emit('[')
        # Not Done Yet
        move_val(IDX_TMP, IDX_EXTRA_2)
        goto(IDX_EXTRA_2); emit('-')
        
        # Check if 0 (Match)
        clear(IDX_IS_MATCH); emit('+')
        goto(IDX_EXTRA_2); emit('[')
        goto(IDX_IS_MATCH); emit('-') # Match=0 marker manipulation
        emit('-') # Decrement for next pass
        goto(IDX_TMP); emit('+') # Restore remaining
        goto(IDX_EXTRA_2)
        emit(']')
        
        goto(IDX_IS_MATCH)
        emit('[')
        # MATCHED!
        action_func()
        goto(IDX_FLAG); emit('+') # Set Done_Flag=1
        goto(IDX_IS_MATCH); emit('-')
        emit(']')
        
        clear(IDX_EXTRA)
        emit(']')

    # --- Define Actions ---
    def act_plus():
        goto(IDX_DATA); emit('+')

    def act_minus():
        goto(IDX_DATA); emit('-')

    def act_dot():
        goto(IDX_DATA); emit('.')
        
    def act_scan():
        # Physical Scan Logic:
        # Loop while ScanFlag is 1.
        # Inside loop: Read char. If ']' or 0, Set ScanFlag=0.
        
        clear(IDX_SCAN_FLAG); emit('+')
        
        goto(IDX_SCAN_FLAG)
        emit('[')
        
        # Read next char into IDX_CHAR
        goto(IDX_CHAR); emit(',')
        
        # Check if 0 (EOF)
        # If 0, Stop (Clear ScanFlag)
        copy_val(IDX_CHAR, IDX_EXTRA, IDX_EXTRA_2)
        clear(IDX_IS_MATCH); emit('+')
        goto(IDX_EXTRA); emit('['); goto(IDX_IS_MATCH); emit('-'); goto(IDX_EXTRA); emit('[-]'); emit(']')
        
        goto(IDX_IS_MATCH); emit('[')
        clear(IDX_SCAN_FLAG) # EOF -> Stop
        clear(IDX_IS_MATCH)
        emit(']')
        
        # Check if 8 (])
        # Only if ScanFlag is still 1
        copy_val(IDX_SCAN_FLAG, IDX_EXTRA, IDX_EXTRA_2)
        goto(IDX_EXTRA); emit('[')
        
        copy_val(IDX_CHAR, IDX_EXTRA_2, IDX_EXTRA)
        goto(IDX_EXTRA_2); emit('-'*8)
        
        clear(IDX_IS_MATCH); emit('+')
        goto(IDX_EXTRA_2); emit('['); goto(IDX_IS_MATCH); emit('-'); goto(IDX_EXTRA_2); emit('[-]'); emit(']')
        
        goto(IDX_IS_MATCH); emit('[')
        clear(IDX_SCAN_FLAG) # ] -> Stop
        clear(IDX_IS_MATCH)
        emit(']')
        
        clear(IDX_EXTRA)
        emit(']')
        
        goto(IDX_SCAN_FLAG); emit(']') # Loop
        
        # Done Scanning.
        # The main loop expects us to read the *next* opcode.
        # Note: we read into IDX_CHAR (separate from IDX_OP). The file pointer advanced,
        # so the main loop's next ',' (into IDX_OP) will read the following byte.
        # Therefore no extra consumption needed here.

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

    # Output: map BF to Spaces tokens
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    print("".join([mapping.get(c, '') for c in bf]), end='')

if __name__ == "__main__":
    main()