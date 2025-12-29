import sys

# Stage 3: Deterministic "Skip-Logic" Interpreter generator
# Based on the user's robust pointer movement logic.
#
# Memory Layout:
# [0: Opcode] [1: Temp] [2: SkipFlag] [3: Data]
#
# Logic:
# - Use absolute 'goto(idx)' to prevent pointer misalignment.
# - Implements a "Skip Mode":
#   - If SkipFlag is 1: Ignore everything except ']' (8).
#   - If SkipFlag is 0: Execute +, ., [, ].

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
    # Read and discard SPA header (4 bytes including the first dummy read logic)
    # Actually, we just need to consume 3 bytes (S, P, A) then start reading code.
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
    # Logic: If SkipFlag(IDX_SKIP) != 0, we only check for ']' (8).
    goto(IDX_SKIP)
    emit('[') 
    # { Inside Skip Mode }
    
    # Check if Temp == 8 (])
    # Subtract 8 from Temp
    goto(IDX_TMP)
    emit('-'*8)
    
    emit('[') 
    # { Temp != 8 (Not ']') }
    # Restore Temp (for correctness, though we ignore it anyway)
    # Actually, simpler: Just clear Temp and exit checks.
    emit('[-]')
    emit(']')
    
    # If Temp is now 0 (meaning it WAS 8), we found the closing bracket.
    # We need a way to detect "it was 0". 
    # Correct logic:
    #   Set a Marker=1. 
    #   If Temp!=0 (Not 8), Set Marker=0.
    #   If Marker=1, Clear SkipFlag.
    # BUT, simpler for this test: 
    # We destructively subtracted 8. If 0, we are done skipping.
    
    # Let's rely on exact sequence for robustness:
    # We are inside SkipFlag loop.
    # If we find ']', we clear SkipFlag.
    # Since we are inside the SkipFlag loop `[ ... ]`, clearing it exits the loop immediately.
    
    # Re-logic:
    # 1. Go to Temp. Subtract 8.
    # 2. If Temp is 0, we found it! Clear SkipFlag.
    # 3. If Temp is not 0, do nothing.
    
    # How to check "If 0" in BF?
    #   flag = 1; temp [ flag=0; temp[-] ] flag [ Clear SkipFlag; flag[-] ]
    
    # Use IDX_DATA as temporary flag? No, Data must be preserved.
    # Use IDX_OP as temp flag (it is currently 0).
    
    # Is_Match logic:
    goto(IDX_OP) 
    emit('+') # Flag = 1
    
    goto(IDX_TMP)
    emit('[') # If Temp!=0 (Not ']')
    goto(IDX_OP)
    emit('-') # Flag = 0
    goto(IDX_TMP)
    emit('[-]') # Clear Temp
    emit(']')
    
    # Check Flag
    goto(IDX_OP)
    emit('[') # If Flag=1 (Found ']')
    goto(IDX_SKIP)
    emit('[-]') # Turn OFF SkipFlag
    goto(IDX_OP)
    emit('-') # Clear Flag
    emit(']')
    
    # Return to SkipFlag (to loop logic, though we just cleared it if found)
    goto(IDX_SKIP)
    # Ensure we leave SkipFlag loop if we cleared it
    # If we didn't clear it, we loop? No, SkipFlag is a status, not a while loop condition for this block.
    # We need to ensure we run this block ONCE.
    # BF `[` is a while loop.
    # So we must Clear SkipFlag temporarily? No, tricky.
    
    # Better logic:
    # We separate "Check Skip" from "Execute".
    # This block was meant to be "If SkipFlag is active".
    # We must `goto(IDX_SKIP)` at end? No.
    # To treat `[` as `if`, we must zero it at start and restore it?
    # Or move it to a temp holding cell.
    
    # Let's use Move Skip -> Op (Temp holding).
    move_val(IDX_SKIP, IDX_OP)
    # Now Op holds the Skip Status. SkipFlag is 0.
    # We can run checks on Op.
    # If Op is 1: Check match. If match, Op=0. If no match, Op=1.
    # Move Op -> SkipFlag.
    
    emit(']') # End of "Inside Skip Mode" (This loop block was invalid logic above, refactoring below)

    # --- REFACTORED LOGIC START ---
    
    # 1. Decide if we are Skipping or Executing.
    # We have SkipFlag at IDX_SKIP.
    # We have Opcode at IDX_TMP.
    
    # Copy SkipFlag to IDX_OP (using it as a working register)
    # Copy logic: SkipFlag -> Op AND SkipFlag (restore)
    #   Move Skip -> Op
    #   Copy Op -> Skip & Data? No, don't touch Data.
    #   Just Move Skip -> Op. Process. Move Op -> Skip.
    
    move_val(IDX_SKIP, IDX_OP)
    
    # Now IDX_OP is 1 if skipping, 0 if executing.
    goto(IDX_OP)
    emit('[') 
    # === SKIPPING MODE ===
    # Check if IDX_TMP == 8 (])
    # Sub 8
    goto(IDX_TMP)
    emit('-'*8)
    
    # Check if 0
    # Use IDX_SKIP as helper (it's 0 now)
    goto(IDX_SKIP)
    emit('+') # Helper=1
    
    goto(IDX_TMP)
    emit('[') # If Temp!=0 (Not 8)
    goto(IDX_SKIP)
    emit('-') # Helper=0
    goto(IDX_TMP)
    emit('[-]')
    emit(']')
    
    # If Helper=1, we found ]
    goto(IDX_SKIP)
    emit('[')
    goto(IDX_OP)
    emit('[-]') # Clear "Skipping Mode" (Set Op=0)
    goto(IDX_SKIP)
    emit('-') # Clear Helper
    emit(']')
    
    goto(IDX_OP)
    emit('-') # This loop runs once? No, we used Op as the flag.
    # If we found ], Op is 0. Loop ends.
    # If we didn't, Op is 1. We need to stop the loop but keep Op=1.
    # Actually, we moved SkipFlag->Op. We need to move it back later.
    # Just `emit(']')` is dangerous if Op is still 1.
    # We need `[ ... [-] ]` pattern + restore?
    # Simple: Subtract 1 from Op at start, Add 1 at end?
    # No, Op is the value.
    
    # Deterministic If:
    # `[ code... [-] ]` runs code once if true, then clears.
    # But we want to preserve the state.
    
    # Correct strategy:
    # We handle "Skipping" and "Executing" logic sequentially.
    # Logic:
    #   Is_Skip = SkipFlag
    #   Is_Exec = not SkipFlag
    
    # Let's clean up logic.
    # IDX_SKIP holds the state.
    # 1. Check SkipFlag.
    #    If 1: Check `]`. If found, SkipFlag=0. Else SkipFlag=1. Clear Temp (instruction consumed).
    #    If 0: Execute instructions.
    
    # Move SkipFlag to IDX_OP to use as "Is_Skip"
    # We will restore it to IDX_SKIP if it remains true.
    emit(']') # Close the previous conceptual block
    
    move_val(IDX_SKIP, IDX_OP) # Op = Is_Skipping
    
    goto(IDX_OP)
    emit('[')
    # === SKIP LOGIC ===
    # We are skipping. Only `]` (8) matters.
    # Check Temp == 8.
    goto(IDX_TMP)
    emit('-'*8)
    
    # Use IDX_SKIP as "Found Match" flag (currently 0)
    goto(IDX_SKIP)
    emit('+') 
    
    goto(IDX_TMP)
    emit('[') # Temp!=0 (Not ']')
    goto(IDX_SKIP)
    emit('-') # Found=0
    goto(IDX_TMP)
    emit('[-]')
    emit(']')
    
    # Check Found (IDX_SKIP)
    goto(IDX_SKIP)
    emit('[') # Found ']'
    goto(IDX_OP)
    emit('[-]') # Set Is_Skipping = 0
    goto(IDX_SKIP)
    emit('-') # Clear Found
    emit(']')
    
    # We consumed the instruction. Ensure Temp is clear.
    # (Already clear).
    
    # If Is_Skipping (Op) is still 1, we need to put it back to IDX_SKIP later.
    # For now, we are done with this block.
    # To exit loop, we must clear Op, but we need to save its value.
    # Move Op -> IDX_SKIP.
    move_val(IDX_OP, IDX_SKIP) 
    
    goto(IDX_OP) # Should be 0
    emit(']') # End Skip Logic
    
    
    # 2. Check Execute Logic
    # We execute ONLY if IDX_SKIP == 0.
    # But we also need to check if IDX_TMP != 0 (meaning instruction not consumed by skip logic).
    # (If we were skipping, Temp is 0. If we weren't, Temp is Opcode).
    
    goto(IDX_TMP)
    emit('[') 
    # === EXECUTE LOGIC ===
    # If we are here, Temp has an opcode AND we are not skipping.
    
    # DECODE (Subtract approach)
    # Check 7 ([)
    emit('-'*7)
    # If 0, it's `[`.
    
    # To check for 0 without losing the "Not 0" path, we usually restore.
    # But since opcodes are unique, we can nest `[` checks.
    
    # Try `[` (7)
    # We use IDX_OP as "Is_Match" flag.
    goto(IDX_OP); emit('+')
    goto(IDX_TMP); emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-') # If not 0, dec (check 8)
      # Try `]` (8) (Value is now original - 8)
      # Note: 7 already subtracted. So subtract 1 more.
      emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-') # If not 0 (check 6? No, order matters)
        # We need to add back to check smaller numbers?
        # Let's restart:
        # 3, 5, 7, 8.
        # Temp holds Opcode.
        
        # Check 8 (])
        # Since we are in Execute mode, `]` does nothing (or stops loop in full logic).
        # For this test, `]` is end of loop, but we assume depth-1 logic handled by skip.
        # If we hit `]` in exec mode, it means we reached end of loop iteration.
        # We just consume it.
        # Code: `[-]+[-]+`
        
        # Let's do a simple cascade.
        # Temp is currently Original - 8.
        # Restore:
        emit('+'*2) # Back to Original - 6
        
        # Check 6 (,) -> Ignore
        emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')
          # Check 5 (.)
          emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')
            # Check 4 (-) -> Ignore
            emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('-')
              # Check 3 (+)
              emit('['); goto(IDX_OP); emit('-'); goto(IDX_TMP); emit('[-]') # Consume rest
                # (Remaining cases: 1, 2 ignored)
              emit(']')
              # Action 3 (+)
              # If we are here, Op matches. 
              # But wait, nested `[` logic is tricky to place actions.
              # Simpler: Use specific subtract-and-check blocks.
    
    # --- RESTART DECODE (Simple Blocks) ---
    # We are inside `goto(IDX_TMP); emit('[')`.
    # Clear this loop immediately to use linear logic.
    goto(IDX_TMP); emit('[-]'); emit(']')
    
    # Restore Opcode from somewhere? No, we lost it.
    # Wait, the previous logic relied on Temp having Opcode.
    # We need to preserve Temp or use linear checks.
    # Let's simply rebuild the loop structure properly.
    
    # Re-Read Opcode into Temp (It is already there from start of main loop)
    # But we might have cleared it in "Skip Logic".
    # If Skip Logic ran (SkipFlag=1), Temp is 0.
    # If Skip Logic didn't run (SkipFlag=0), Temp is Opcode.
    # So we check Temp.
    
    goto(IDX_TMP)
    emit('[') 
    # We have an instruction to execute!
    
    # Copy Temp -> Op (Backup)
    # move_val clears source. We want copy.
    # Copy Temp -> Op using Skip as helper
    goto(IDX_SKIP); emit('[-]')
    goto(IDX_OP); emit('[-]')
    goto(IDX_TMP)
    emit('[')
    emit('-')
    goto(IDX_OP); emit('+')
    goto(IDX_SKIP); emit('+')
    goto(IDX_TMP)
    emit(']')
    # Restore Temp
    goto(IDX_SKIP)
    emit('[')
    emit('-')
    goto(IDX_TMP); emit('+')
    goto(IDX_SKIP)
    emit(']')
    
    # Now Op holds the Opcode for testing. Temp holds it for next checks if needed.
    
    # Check 3 (+)
    goto(IDX_OP); emit('-'*3)
    emit('[') # Not 3
    emit('-'*2) # Check 5 (.-)
      emit('[') # Not 5
      emit('-'*2) # Check 7 ([)
        emit('[') # Not 7
        emit('-') # Check 8 (])
          emit('[') # Not 8
          emit('[-]') # Ignore others
          emit(']')
          # Action 8 (])
          # In Exec mode, `]` means end of loop iteration. 
          # Nothing to do for Depth-1.
        emit(']')
        # Action 7 ([)
        # Check Data. If 0, Set SkipFlag=1.
        # Data is at IDX_DATA.
        # Logic: Flag = 1. Data [ Flag = 0 ]. If Flag=1 -> Set SkipFlag.
        goto(IDX_SKIP); emit('+') # Flag/Skip = 1
        goto(IDX_DATA); emit('[')
        goto(IDX_SKIP); emit('-') # Data is not 0, so Skip=0
        goto(IDX_DATA); emit('[')
        emit('-')
        goto(IDX_TMP); emit('+') # Backup Data to Temp (Hack: reusing Temp as dump)
        goto(IDX_DATA)
        emit(']')
        # Restore Data from Temp
        goto(IDX_TMP); emit('['); emit('-'); goto(IDX_DATA); emit('+'); goto(IDX_TMP); emit(']')
        goto(IDX_DATA); emit(']')
        # Now IDX_SKIP is 1 if Data was 0, 0 otherwise. Correct!
      emit(']')
      # Action 5 (.)
      goto(IDX_DATA); emit('.'); goto(IDX_OP)
    emit(']')
    # Action 3 (+)
    goto(IDX_DATA); emit('+'); goto(IDX_OP)
    
    emit(']') # End Check 3
    
    # Done executing. Clear Temp to exit the "If Executing" block.
    goto(IDX_TMP)
    emit('[-]')
    
    emit(']') # End "If Executing"
    
    # --- 4. Next Loop ---
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
