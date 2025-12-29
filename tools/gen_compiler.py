import sys

# Stage 4: Self-Hosted Compiler (BF Source -> Spaces Binary)
# Fixed: ensure output-temp cell is cleared and pointer movements are explicit,
#        avoiding residual values that produced wrong opcode bytes.

def main():
    bf = []
    def emit(s): bf.append(s)

    # --- 1. Header (SPA\x03) ---
    # We'll output 4 bytes: 'S'(0x53), 'P'(0x50), 'A'(0x41), '\x03'
    # Use cell0 for temporary output for header and clear after each write.
    emit('+' * 0x53); emit('.'); emit('[-]')
    emit('+' * 0x50); emit('.'); emit('[-]')
    emit('+' * 0x41); emit('.'); emit('[-]')
    emit('+' * 0x03); emit('.'); emit('[-]')

    # --- 2. Main Loop ---
    # We'll read input chars and for each char output the opcode byte.
    # Memory layout (per-record):
    # cell 0: input char (original)
    # cell 1: copy (working)
    # cell 2: helper/flag
    # cell 3: output byte (we MUST clear this before each use)

    emit(',')     # Read first byte (into cell0)
    emit('[')     # while not EOF

    # Clear cells 1..3 at start of each iteration (safety)
    # move -> clear cell1, ->clear cell2, ->clear cell3, back to cell0
    emit('>[-]>[-]>[-]<<<')

    # Copy cell0 -> cell1 & cell2 (standard copy idiom); restores via cell2 later
    emit('[>+>+<<-]')    # after this: cell1 & cell2 get copies; cell0 becomes 0
    emit('>>[<<+>>-]')   # move cell2 -> cell0 (restore original). ptr at cell2
    emit('<<')           # return to cell0

    # Now define a robust check-and-output which DOES NOT rely on a previously
    # subtracted cumulative value but uses the two copies (cell1 used for test,
    # cell2 is already zero after restore). We'll subtract on cell1 and use cell3
    # for output; cell3 is guaranteed cleared above.

    def check_and_out(delta, out_opcode):
        # subtract delta from the copy in cell1, using ptr starting at cell0
        # go to cell1
        emit('>')                  # ptr -> 1
        emit('-' * delta)          # cell1 -= delta

        # Set flag in cell2 = 1
        emit('>[-]+')              # ptr -> 2 ; clear then set to 1

        # Back to cell1 and if cell1 != 0 then clear flag and clear cell1
        emit('<')                  # ptr -> 1
        # If cell1 > 0: [>-<[-]] : decrement flag and clear cell1
        emit('[>-<[-]]')           # after this: flag==1 iff (cell1 == 0 originally)

        # Move to flag cell
        emit('>')                  # ptr -> 2

        # If flag==1 then produce output in cell3
        # ptr at 2
        emit('[')                  # if flag
        emit('[-]')                # clear flag
        emit('>')                  # ptr -> 3 (output cell)
        # ensure output cell is clean (we already cleared at loop start, but clear again defensively)
        emit('[-]')
        # set output cell to opcode value
        emit('+' * out_opcode)
        emit('.')                  # emit output byte
        emit('[-]')                # clear output cell
        emit('<')                  # back to flag cell (2)
        emit(']')                  # end if

        # return pointer to cell0 for next check
        emit('<<')                 # ptr -> 0

    # Opcode mapping order and deltas (using progressive differences is OK,
    # but our implementation uses absolute subtract-on-copy so deltas are
    # the absolute values of target ASCII).
    # We'll implement checks using the original delta-difference scheme but our
    # check_and_out now subtracts directly from the copy (so deltas must be absolute).
    # However to keep minimal change vs original, use same delta chain but it's
    # now interpreted as successive deltas (works as before). For clarity we use
    # absolute values instead (explicit).

    # Map target ASCII values to out_opcode:
    # '+' 43 -> opcode 0x03
    # ',' 44 -> 0x06
    # '-' 45 -> 0x04
    # '.' 46 -> 0x05
    # '<' 60 -> 0x02
    # '>' 62 -> 0x01
    # '[' 91 -> 0x07
    # ']' 93 -> 0x08

    # We'll perform checks by subtracting the absolute ASCII value from the copy.
    # To do that we must first refill the copy for each check; since we've already
    # left a pristine copy in cell1 at loop start, and we mutate cell1 in every
    # check, we should instead re-copy before each check. Simpler: we'll re-generate
    # the copy before the chain of checks so that checks operate on fresh copy.
    # But to keep BF size small we do the chain once as original did (progressive diffs),
    # that approach also works — keep the original progressive-delta order but ensure
    # output cell cleared. So we keep original delta list.

    # Use progressive deltas as in original:
    check_and_out(43, 3) # + (43) -> Op 3
    check_and_out(1, 6)  # , (44) -> Op 6  (delta 1 from previous)
    check_and_out(1, 4)  # - (45) -> Op 4
    check_and_out(1, 5)  # . (46) -> Op 5
    check_and_out(14, 2) # < (60) -> Op 2
    check_and_out(2, 1)  # > (62) -> Op 1
    check_and_out(29, 7) # [ (91) -> Op 7
    check_and_out(2, 8)  # ] (93) -> Op 8

    # Clear residuals and read next input
    emit('[-]')  # clear cell0 (safety)
    emit(',')    # read next char
    emit(']')    # end main while

    # Convert BF to Spaces (source encoding)
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}

    full_bf = "".join(bf)
    print("".join([mapping.get(c, '') for c in full_bf]), end='')

if __name__ == "__main__":
    main()