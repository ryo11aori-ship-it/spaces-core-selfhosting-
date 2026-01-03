#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler (Self-Hosting Linear)
# Strategy: Use a fixed OUTPUT_CELL to prevent pointer corruption.
#           Standard Python indentation to ensure no syntax errors.

import sys

# --- Spaces Dialect Primitives ---
S = " "
F = "\u3000"

def emit(s):
    sys.stdout.write(s + "\n")

def right(n=1):
    if n > 0: emit((S+S+S) * n)

def left(n=1):
    if n > 0: emit((S+S+F) * n)

def inc(n=1):
    if n > 0: emit((S+F+S) * n)

def dec(n=1):
    if n > 0: emit((S+F+F) * n)

def out():
    emit(F + S + S)

def inp():
    emit(F + S + F)

def loop_open():
    emit(F + F + S)

def loop_close():
    emit(F + F + F)

def clear():
    loop_open()
    dec()
    loop_close()

# --- Memory Layout ---
# Cell 100: Input Data (Current Char)
# Cell 101: Temp 1
# Cell 102: Temp 2
# ...
# Cell 200: OUTPUT_CELL (Used for printing bytes)

DATA_CELL = 100
OUTPUT_CELL = 200

# Helper to output a byte using the dedicated OUTPUT_CELL
# Assumption: We start at DATA_CELL and must return to DATA_CELL.
def emit_byte_literal(val):
    # Move to OUTPUT_CELL
    right(OUTPUT_CELL - DATA_CELL)
    
    # Clear and Set Value
    clear()
    inc(val)
    
    # Output
    out()
    
    # Return to DATA_CELL
    left(OUTPUT_CELL - DATA_CELL)

def emit_bytes_literal(vals):
    for v in vals:
        emit_byte_literal(v)

# Dense Switch Logic
# Checks if current cell (DATA_CELL) matches expected char code.
# The 'delta' is how much to subtract from the *current* value of DATA_CELL.
# If DATA_CELL becomes 0, it's a match.
def check_and_emit(delta, code_bytes):
    # 1. Subtract delta from DATA_CELL
    dec(delta)
    
    # 2. Check if DATA_CELL is 0 using Temp 1 (Cell 101)
    # Move to Temp 1
    right(1)
    clear()
    inc() # Temp1 = 1 (Default: assume match/zero)
    left(1)
    
    # If DATA_CELL != 0, Set Temp1 = 0
    loop_open()
    right(1)
    dec() # Temp1 = 0
    left(1)
    # We need to preserve DATA_CELL for next checks if it's not 0.
    # Non-destructive check trick:
    # Move DATA_CELL to Temp 2 (102) to break the loop, then restore.
    right(2); inc(); left(2) # Move to Temp2
    dec() # Decrement DATA_CELL to 0 to exit loop
    loop_close()
    
    # Restore DATA_CELL from Temp 2
    right(2)
    loop_open()
    left(2); inc(); right(2); dec()
    loop_close()
    left(2)
    
    # 3. Now check Temp 1. If 1, it matched.
    right(1)
    loop_open()
    # Match detected! Emit code.
    dec() # Clear Temp 1
    left(1) # Go back to DATA_CELL
    
    emit_bytes_literal(code_bytes)
    
    right(1) # Go back to Temp 1 to exit loop
    loop_close()
    left(1) # Return to DATA_CELL

def main():
    target_file_size = 500
    load_addr = 0x400000
    
    def p64(v): return list(v.to_bytes(8, "little"))
    def p32(v): return list(v.to_bytes(4, "little"))

    header = [
        0x7f,0x45,0x4c,0x46,0x02,0x01,0x01,0x00,0,0,0,0,0,0,0,0,
        0x02,0x00,0x3e,0x00,0x01,0x00,0x00,0x00,
        *p64(load_addr + 120), *p64(64), *p64(0), *p32(0),
        0x40,0x00,0x38,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    ]
    prog_header = [
        0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(target_file_size), *p64(0x10000), *p64(0x1000)
    ]
    
    # --- GENERATE SPACES CODE ---
    
    # 1. Initialize Pointers
    # We start at 0. Move to DATA_CELL.
    right(DATA_CELL)
    
    # 2. Emit ELF Header (Always output first)
    emit_bytes_literal(header + prog_header)
    emit_bytes_literal([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00]) # Code stub
    
    # 3. Main Input Loop
    # We use a Flag at DATA_CELL+5 (105) to control the loop.
    right(5)
    inc() # Flag = 1
    loop_open()
    left(5) # Back to DATA_CELL
    
    # Read Char
    inp()
    
    # EOF Check: If DATA_CELL is 0, we exit.
    # We use Temp 1 (101) as EOF flag.
    # Copy DATA to Temp 1.
    loop_open(); right(1); inc(); left(1); dec(); loop_close() # Move
    right(1); loop_open(); left(1); inc(); right(1); dec(); loop_close(); left(1) # Restore
    
    # Check Temp 1. If 0 (EOF), set Flag (105) to 0.
    # We actually need inverted logic: If Temp 1 != 0, Keep Flag=1. If 0, Set Flag=0.
    # But Flag is already 1. So if Temp 1 == 0, we zero Flag.
    
    # Logic: Set IsEOF(102) = 1. If Temp1(101) != 0, Set IsEOF = 0.
    right(2); inc(); left(1) # IsEOF=1. At Temp1.
    loop_open()
    right(1); dec(); left(1) # IsEOF=0
    clear() # Clear Temp1
    loop_close()
    
    # Now check IsEOF (102).
    right(2)
    loop_open()
    # EOF DETECTED!
    
    # 1. Emit Exit Syscall & Padding (Flush)
    left(2) # Back to DATA
    emit_bytes_literal([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    # Emit 250 zeros for padding
    for _ in range(250):
        emit_byte_literal(0)
    right(2) # Back to IsEOF
        
    # 2. Kill Main Loop Flag (105)
    right(3); dec(); left(3)
    
    # 3. Kill IsEOF (102)
    dec()
    loop_close()
    left(2) # Back to DATA_CELL
    
    # Dense Switch for Commands
    # Sorted: + (43), , (44), - (45), . (46), < (60), > (62), [ (91), ] (93)
    
    check_and_emit(43, [0xfe, 0x03]) # +
    check_and_emit(1, [0xb8, 0x00, 0x00, 0x00, 0x00, 0xbf, 0x00, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]) # ,
    check_and_emit(1, [0xfe, 0x0b]) # -
    check_and_emit(1, [0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]) # .
    check_and_emit(14, [0x48, 0xff, 0xcb]) # <
    check_and_emit(2, [0x48, 0xff, 0xc3]) # >
    
    # Skip [ and ]
    dec(29)
    dec(2)
    
    # Clean up residual value in DATA_CELL for next iteration
    clear()
    
    # End Main Loop
    right(5)
    loop_close()

if __name__ == "__main__":
    main()
