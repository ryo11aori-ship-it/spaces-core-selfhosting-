import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Strategy:
# - Emit SPA header as before.
# - For each input byte (BF source char), explicitly test against each BF command
#   by re-copying the original and subtracting the candidate ASCII value.
# - If equal, write the corresponding opcode byte (1..8) via output cell.
#
# This is naive but reliable and self-contained as a BF program (encoded to Spaces).

def main():
    bf = []
    def emit(s): bf.append(s)

    # --- Header: 'S' 'P' 'A' 0x03 ---
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')
    emit('+' * 0x03); emit('.'); emit('[-]')

    # --- Main loop: read input char-by-char and output opcode ---
    # Memory layout per iteration:
    # cell0: input char (original)
    # cell1: working copy
    # cell2: flag / helper
    # cell3: output byte (cleared before use)

    emit(',')   # read first char into cell0
    emit('[')   # while cell0 != 0

    # We'll loop through each candidate and do:
    #   - clear cells 1..3
    #   - copy cell0 -> cell1 (preserve cell0)
    #   - subtract candidate from cell1
    #   - set flag and test; if zero -> output opcode in cell3
    # After checking all candidates, read next char.

    def candidate_block(ascii_val, out_opcode):
        """
        Emit BF snippet that:
         - re-copies original from cell0 to cell1
         - subtracts ascii_val from cell1
         - if zero: set cell3 to out_opcode and output it
         - always returns pointer to cell0
        Assumes pointer at cell0 at entry.
        """
        s = []
        # 1) Clear cells 1,2,3 defensively, then return to cell0
        s.append('>[-]>[-]>[-]<<<')

        # 2) Copy cell0 -> cell1 & cell2, restore cell0 (common copy idiom)
        s.append('[>+>+<<-]')    # cell0 -> cell1,cell2 ; cell0 = 0
        s.append('>>[<<+>>-]')   # move cell2 -> cell0 ; cell2 = 0 ; ptr at cell2
        s.append('<<')           # ptr -> cell0

        # 3) Move to cell1 and subtract ascii_val
        s.append('>')            # ptr -> cell1
        if ascii_val > 0:
            s.append('-' * ascii_val)  # destructive subtraction on cell1

        # 4) Set flag in cell2 = 1
        s.append('>[-]+')        # ptr -> cell2 ; clear then set to 1

        # 5) If cell1 != 0 then clear flag and clear cell1
        s.append('<')            # ptr -> cell1
        s.append('[>-<[-]]')     # if cell1>0 then flag-- and clear cell1

        # 6) If flag == 1 -> produce output in cell3
        s.append('>')            # ptr -> cell2 (flag)
        s.append('[')            # if flag
        s.append('[-]')          # clear flag
        s.append('>')            # ptr -> cell3 (output cell)
        s.append('[-]')          # ensure clean
        if out_opcode > 0:
            s.append('+' * out_opcode)   # set output cell to opcode value
        s.append('.')            # emit output byte
        s.append('[-]')          # clear output cell
        s.append('<')            # back to flag
        s.append(']')            # end if

        # 7) Return pointer to cell0
        s.append('<<')           # ptr -> cell0

        return "".join(s)

    # Candidate list: (char, ascii, opcode)
    candidates = [
        ('+', 43, 3),
        (',', 44, 6),
        ('-', 45, 4),
        ('.', 46, 5),
        ('<', 60, 2),
        ('>', 62, 1),
        ('[', 91, 7),
        (']', 93, 8),
    ]

    # Emit candidate checks in a stable order
    for ch, ascii_val, opcode in candidates:
        bf_block = candidate_block(ascii_val, opcode)
        emit(bf_block)

    # After checking all candidates, clear cell0 and read next char
    # (We keep cell0 intact between checks; clearing ensures no stray values)
    emit('[-]')
    emit(',')      # read next char
    emit(']')      # end main loop

    # Convert BF program to Spaces encoding
    S, F = " ", "\u3000"
    mapping = {
        '>': S*3, '<': S*2+F, '+': S+F+S, '-': S+F+F,
        '.': F+S+S, ',': F+S+F, '[': F*2+S, ']': F*3
    }

    full_bf = "".join(bf)
    # Map any BF characters in full_bf; if other chars appear (none should), ignore.
    out = []
    for c in full_bf:
        if c in mapping:
            out.append(mapping[c])
    sys.stdout.write("".join(out))

if __name__ == "__main__":
    main()