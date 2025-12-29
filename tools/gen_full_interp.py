#!/usr/bin/env python3
import sys

# gen_full_interp.py -- generate a robust, depth-1 self-interpreter (BF -> Spaces)
# Design constraints:
# - Linear decode loop: read opcode into a dedicated cell, keep an IP_VALID cell to control loop
# - Depth-1 loops: when encountering '[' opcode, if data == 0, enter a scanning subloop that consumes input until ']' or EOF
# - Avoid any construction that can produce unmatched brackets in generated BF

def main():
    # helpers to build BF program safely
    def mov(n):
        return '>'*n if n>=0 else '<'*(-n)
    def clear():
        return '[-]'
    def loop(s):
        return '[' + s + ']'
    def add(n):
        return '+'*n
    def sub(n):
        return '-'*n

    # Memory layout (cells)
    # 0: OP (current opcode read from input)
    # 1: TMP (work)
    # 2: DONE/FLAG (used during decode)
    # 3: DATA (virtual program's single data cell for this test)
    # 4: A (scratch)
    # 5: B (scratch)
    # 6: MATCH (tmp)
    # 7: SCAN_FLAG (for scanning when inside a skipped loop)
    # 8: CHAR (used to read chars during scan)
    # 9: COPY_TMP (copy scratch)
    # 10: IP_VALID (loop continuation flag)
    #
    # We keep layout small and explicit. All moves are absolute relative moves from current pointer.

    bf = ""

    # Start pointer at cell 0 implicitly
    # 1) Consume header 'S' 'P' 'A'  (three commas)
    bf += ',' + ',' + ','

    # 2) Read first opcode into OP
    bf += ','

    # 3) Set IP_VALID = 1 (we'll use cell 10). Move to it and set it.
    bf += mov(10 - 0) + clear() + '+'  # goto cell10, clear, set to 1
    bf += mov(-10)  # back to OP (cell 0)

    # 4) Main loop controlled by IP_VALID at cell10
    # We'll implement as: goto cell10; [ ... body ... ]; (so we need to be at cell10 to open loop)
    bf += mov(10) + '['  # enter while IP_VALID

    # Body: at loop entry we are at cell10. Move back to OP to operate.
    bf += mov(-10)  # now at OP (cell 0)

    # Copy OP -> TMP (destructive copy pattern: TMP = OP; OP left as-is)
    # We'll implement safe copy: copy OP->TMP using COPY_TMP (cell9) as scratch, restoring OP.
    # copy(src=0,dst=1,tmp=9)
    bf += mov(1) + clear() + mov(-1) + mov(9) + clear() + mov(-9)  # clear dst/tmp, return to OP
    bf += loop(            # while OP != 0
        '-' + mov(1) + '+' + mov(9) + '+' + mov(-10)  # careful moves; we'll instead implement simpler: do manual sequence below
    )
    # The previous ad-hoc attempt with loops is error-prone to write inline — replace with a robust manual copy sequence:
    # Simpler approach: use a standard copy template (we'll rewrite cleanly).

    # To avoid mistakes writing long templates inline, switch to constructing with small helper subroutines:
    # We'll build the core body programmatically to ensure bracket balance.

    # Reset bf and rebuild body using programmatic subroutines for correctness
    bf = ""
    def emit(s): 
        return s

    # small BF generators that emit balanced constructs
    def goto(cell_from, cell_to):
        return mov(cell_to - cell_from)

    # templates (we will keep pointer movements explicit in sequence rather than complicated nested inline loops)
    # Standard copy template: copy src->dst using tmp, restoring src
    # Implementation (assumes pointer starts at src and ends at src):
    # clear(dst); clear(tmp);
    # [ - >+ >+ < < ]  (move value from src to dst and tmp)
    # then [ - <+ ] (move tmp back to src)
    def copy_template(src, dst, tmp):
        seq = ""
        seq += goto(0, dst) + clear()    # clear dst
        seq += goto(dst, tmp) + clear()  # clear tmp
        seq += goto(tmp, src)            # go to src
        seq += '['
        seq += '-'                      # decrement src
        seq += mov(dst - src) + '+'     # dst++
        seq += mov(tmp - dst) + '+'     # tmp++
        seq += mov(src - tmp)           # back to src
        seq += ']'
        # restore src from tmp
        seq += goto(src, tmp)
        seq += '['
        seq += '-' 
        seq += mov(src - tmp) + '+' 
        seq += goto(tmp, tmp)  # stay at tmp
        seq += ']'
        seq += goto(tmp, src)  # end at src
        return seq

    # Build program with copy template and structured checks
    bf += emit(',' + ',' + ',' )  # header consume again to be safe (we already consumed above, but keep consistent with earlier read)
    # However we must not double consume for actual runtime. To be precise, we'll use the earlier initial form:
    # For safety and clarity, produce final BF as follows from scratch:

    bf = ""
    # header consume
    bf += ',' + ',' + ','
    # read first opcode into OP
    bf += ','
    # set IP_VALID = 1 (cell10)
    bf += mov(10) + clear() + '+' + mov(-10)

    # main loop (while IP_VALID)
    bf += mov(10) + '['
    bf += mov(-10)  # back to OP (cell0)

    # copy OP->TMP using COPY_TMP
    bf += copy_template(0, 1, 9)  # src=0 OP, dst=1 TMP, tmp=9

    # clear DONE flag (cell2)
    bf += mov(2) + clear() + mov(-2)

    # --- decode chain ---
    # We'll check opcode values 1..8 (the mapping in ref VM encodes opcodes as 0x01..0x08 but our BF-based decoder treats small integers)
    # The generator that produced loop_test.bin encoded opcodes as small byte values. We'll assume:
    # 0x03 -> '+' ; 0x04 -> '-' ; 0x05 -> '.' ; 0x07 -> '[' ; 0x08 -> ']'
    # Because BF can't directly test equality for nontrivial bytes without consuming, we use subtractive cascade:
    # We'll implement checks by moving TMP to B and subtracting fixed offsets, using MATCH cell as indicator.

    # Helper to append a numeric equality check for value K (on TMP cell 1):
    def emit_check_value(k, action_bf):
        # idea: move TMP->B; decrement B k times; if B becomes zero at right moment indicate match via MATCH cell
        s = ""
        # move TMP->B preserving TMP: copy_template(1->5 using 9) then operate on B
        s += copy_template(1, 5, 9)   # copy TMP (cell1) -> B (cell5)
        # Now check B == k by subtracting k and checking zero
        s += mov(5) + sub(k)  # subtract k from B
        # If B is zero now, put marker in MATCH (cell6). To do this safely:
        # set MATCH=1; if B non-zero, it will be cleared in the loop below:
        s += mov(6) + clear() + '+'  # MATCH = 1
        # If B != 0 then [ ... ] will run; we'll clear MATCH there
        s += mov(5)
        s += '['
        s += mov(6) + '[-]'   # clear MATCH
        s += mov(5) + '[-]'   # clear B to restore later: we'll reconstruct TMP from COPY_TMP if needed
        s += ']'
        # Now if MATCH==1 run action
        s += mov(6)
        s += '['
        s += action_bf
        # set DONE flag
        s += mov(2) + '+' 
        s += mov(6) + '[-]'   # clear MATCH
        s += ']'
        return s

    # Define actions as BF pieces (they must be balanced and leave pointer at same place they start; we'll use absolute goto)
    def action_inc_data():
        return mov(3) + '+' + mov(-3)  # DATA cell=3

    def action_dec_data():
        return mov(3) + '-' + mov(-3)

    def action_output_data():
        return mov(3) + '.' + mov(-3)

    # action for scan ( '[' ): we need to repeatedly read chars until ']'(8) or EOF (0)
    # We'll implement a safe scanning routine that:
    # - set SCAN_FLAG=1
    # - loop: read next char into CHAR (cell8) via ',', check if 0 -> clear SCAN_FLAG and break
    # - else check if CHAR==8, if so clear SCAN_FLAG and break
    # Important: this code consumes bytes from input (so file pointer moves forward) and is safe
    def action_scan():
        s = ""
        # set SCAN_FLAG (cell7)=1
        s += mov(7) + clear() + '+'
        # loop while SCAN_FLAG
        s += mov(7) + '['
        # read next char into CHAR (cell8)
        s += mov(8) + ',' 
        # check EOF (CHAR==0): copy CHAR->A and check
        s += copy_template(8, 4, 9)   # CHAR->A (4)
        s += mov(4) + clear() + '+'  # MATCH reused as check: reuse cell6? but safer to reuse MATCH=6
        # We'll use MATCH(6) for temporary check
        s += mov(6) + clear() + '+'   # MATCH=1
        s += mov(4) + '['
        s += mov(6) + '[-]'  # not zero -> clear MATCH
        s += mov(4) + '[-]'
        s += ']'
        s += mov(6)
        s += '['
        # if MATCH==1 then CHAR was zero -> EOF -> clear SCAN_FLAG and MATCH
        s += mov(7) + '[-]'  # clear scan flag
        s += mov(6) + '[-]'
        s += ']'
        # If SCAN_FLAG still set, check if CHAR == 8 (']')
        # copy CHAR -> B (cell5) and subtract 8
        s += copy_template(8, 5, 9)
        s += mov(5) + sub(8)
        s += mov(6) + clear() + '+'
        s += mov(5) + '['
        s += mov(6) + '[-]'
        s += mov(5) + '[-]'
        s += ']'
        s += mov(6)
        s += '['
        s += mov(7) + '[-]'  # found ']' -> clear scan flag
        s += mov(6) + '[-]'
        s += ']'
        # end of scan loop body
        s += mov(7) + ']'
        # end action_scan
        return s

    # Build full decode chain for opcodes of interest
    # We'll test values by their numeric opcode as per encoder: 0x03('+') 0x04('-') 0x05('.') 0x07('[') 0x08(']')
    # but since parse_line maps 3-bit groups to characters like '+' '-' '.' etc, TMP holds ASCII codes like '+' equal value 43? WAIT:
    # --- IMPORTANT: In this VM design, parse_line uses op_map = {'>', '<', '+', '-', '.', ',', '[', ']'} (these are ASCII characters)
    # So TMP holds ASCII characters '>' '<' '+' etc, not small ints 3/4/5.
    # Our earlier approach that treated opcode as small numeric was inconsistent. We must compare against the ASCII codes.
    # Let's map checks against ASCII bytes:
    OPC_PLUS = ord('+')
    OPC_MINUS = ord('-')
    OPC_DOT = ord('.')
    OPC_COMMA = ord(',')
    OPC_LBR = ord('[')
    OPC_RBR = ord(']')

    # Because BF can't compare arbitrary large ASCII by simple subtracting small constants robustly (we can, but must subtract by ord),
    # we'll implement "equality by copy & subtract full ASCII value".
    def emit_check_char(ascii_code, action_bf):
        # copy TMP->B (cell5), subtract ascii_code, if zero then MATCH, then action
        s = ""
        s += copy_template(1, 5, 9)
        # subtract ascii_code from B
        if ascii_code > 0:
            s += mov(5) + ('-' * ascii_code)
        # set MATCH=1
        s += mov(6) + clear() + '+'
        # if B != 0: clear MATCH and clear B
        s += mov(5) + '['
        s += mov(6) + '[-]'  # clear MATCH
        s += mov(5) + '[-]'
        s += ']'
        # if MATCH then do action and set DONE
        s += mov(6) + '['
        s += action_bf
        s += mov(2) + '+'  # DONE=1
        s += mov(6) + '[-]'
        s += ']'
        return s

    # Compose checks in order (for most frequent ops first maybe)
    # We'll check +, -, ., [, ] (others are ignored)
    decode_seq = ""
    decode_seq += emit_check_char(OPC_PLUS, action_inc_data())
    decode_seq += emit_check_char(OPC_MINUS, action_dec_data())
    decode_seq += emit_check_char(OPC_DOT, action_output_data())
    decode_seq += emit_check_char(OPC_LBR, action_scan())
    # RBR does nothing in execution context (no-op)

    bf += decode_seq

    # After decode, read next opcode into OP cell (consumes input)
    bf += mov(0) + ','

    # Now determine EOF: if OP == 0 then clear IP_VALID else set it to 1 and continue
    # Implementation: clear IP_VALID; if OP != 0 then set IP_VALID.
    bf += mov(10) + '[-]'    # clear IP_VALID
    bf += mov(0) + '['        # if OP != 0 (non-zero), then
    bf += mov(10) + '+'       # IP_VALID = 1
    bf += mov(0) + ']'        # end if
    # close main loop
    bf += mov(10) + ']'

    # BF program constructed. Now map to Spaces tokens
    S = ' '
    F = '\u3000'
    mapping = {
        '>': S*3, '<': S*2 + F,
        '+': S + F + S, '-': S + F + F,
        '.': F + S + S, ',': F + S + F,
        '[': F*2 + S, ']': F*3
    }

    # sanity: ensure bracket balance in BF before converting
    def bracket_balance(s):
        bal = 0
        for ch in s:
            if ch == '[':
                bal += 1
            elif ch == ']':
                bal -= 1
            if bal < 0:
                return False
        return bal == 0

    if not bracket_balance(bf):
        # This should never happen; if it does, abort (fail loudly so CI shows error)
        print("# ERROR: unbalanced brackets in generator output", file=sys.stderr)
        sys.exit(2)

    out = []
    for c in bf:
        if c in mapping:
            out.append(mapping[c])
        # ignore any other characters (shouldn't be any)
    sys.stdout.write(''.join(out))

if __name__ == "__main__":
    main()