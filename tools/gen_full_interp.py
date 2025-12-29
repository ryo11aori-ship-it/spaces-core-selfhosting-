import sys

# Stage 3: Deterministic "Skip-Logic" Interpreter generator
# Fixed: Added guards to actions so they only run on match.

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
    IDX_SKIP = 2
    IDX_DATA = 3

    # --- 1. Header Consumption ---
    goto(IDX_OP)
    emit(',,,')

    # --- 2. Main Loop Setup ---
    goto(IDX_OP)
    emit(',') 
    emit('[')

    move_val(IDX_OP, IDX_TMP)

    # --- 3. Check SkipFlag ---
    move_val(IDX_SKIP, IDX_OP)
    
    goto(IDX_OP)
    emit('[') 
    # === SKIPPING MODE ===
    goto(IDX_TMP); emit('-'*8)
    
    goto(IDX_SKIP); emit('+') # Found=1
    goto(IDX_TMP); emit('['); goto(IDX_SKIP); emit('-'); goto(IDX_TMP); emit('[-]'); emit(']')
    
    goto(IDX_SKIP); emit('['); goto(IDX_OP); emit('[-]'); goto(IDX_SKIP); emit('-'); emit(']')
    
    move_val(IDX_OP, IDX_SKIP) 
    goto(IDX_OP); emit(']') 
    
    # --- 4. Execute Logic ---
    goto(IDX_TMP)
    emit('[') 
    # === EXECUTE MODE ===
    
    # Check 7 ([)
    emit('-'*7)
    
    goto(IDX_OP); emit('+') # Match=1
    goto(IDX_TMP); emit('[') # If Not 7
    goto(IDX_OP); emit('-') # Match=0
    goto(IDX_TMP); emit('-') # Check 8 (])
    
      # Check 8 (])
      emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')
      emit('+'*2) # Restore for 6
      
        # Check 6 (,)
        emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')
        
          # Check 5 (.)
          emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')
          
            # Check 4 (-)
            emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')
            
              # Check 3 (+)
              emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('[-]'); emit(']')
              
              # Action 3 (+)
              goto(IDX_OP); emit('[') # IF MATCH
              goto(IDX_DATA); emit('+')
              goto(IDX_OP); emit('-') # Clear Match
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
        
      emit(']') # End Check 8
      # Action 8 (]) - Ignore
      goto(IDX_OP); emit('[')
      emit('-')
      emit(']')
      
    emit(']') # End Check 7
    
    # Action 7 ([)
    goto(IDX_OP); emit('[')
    
    goto(IDX_SKIP); emit('+') # Assume Skip
    goto(IDX_DATA); emit('[') # If Data!=0
    goto(IDX_SKIP); emit('-') # No Skip
    goto(IDX_DATA); emit('[')
    emit('-')
    goto(IDX_TMP); emit('+') 
    goto(IDX_DATA); emit(']')
    goto(IDX_TMP); emit('['); emit('-'); goto(IDX_DATA); emit('+'); goto(IDX_TMP); emit(']')
    goto(IDX_DATA); emit(']')
    
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
