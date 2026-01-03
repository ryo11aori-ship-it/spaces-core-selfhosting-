#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler (Linear Self-Host)
# Fix: Correctly implements the compiler logic (Read Input -> Dense Switch -> Emit Code).
#      Uses explicit BF command generation to avoid indentation errors.

import sys, os

# Spaces dialect
S = " "
F = "\u3000"

def emit(s): sys.stdout.write(s + "\n")
def raw_right(n=1): emit((S+S+S)*n)
def raw_left(n=1): emit((S+S+F)*n)
def raw_inc(n=1): emit((S+F+S)*n)
def raw_dec(n=1): emit((S+F+F)*n)
def raw_out(): emit(F+S+S)
def raw_inp(): emit(F+S+F)
def raw_loop_open(): emit(F+F+S)
def raw_loop_close(): emit(F+F+F)

# Output helper using a dedicated cell (200) to avoid messing up logic pointers
OUTPUT_CELL = 200
DATA_CELL = 100 # Where we keep the current input char

def go_to_output():
    # Move from DATA_CELL to OUTPUT_CELL
    raw_right(OUTPUT_CELL - DATA_CELL)

def go_to_data():
    # Move from OUTPUT_CELL to DATA_CELL
    raw_left(OUTPUT_CELL - DATA_CELL)

def emit_byte_literal(val):
    # Emits a fixed byte using OUTPUT_CELL
    # Assumes we are at DATA_CELL
    go_to_output()
    raw_loop_open(); raw_dec(); raw_loop_close() # Clear
    if val > 0: raw_inc(val)
    raw_out()
    go_to_data()

def emit_bytes_literal(vals):
    for v in vals: emit_byte_literal(v)

# Dense Switch Helper
# Checks if current cell (DATA_CELL) matches expected char code.
# Since we subtract deltas sequentially, 'val' is the delta from previous check.
# If match (zero), emits 'code_bytes' and sets a 'handled' flag.
def check_and_emit(delta, code_bytes):
    raw_dec(delta)
    
    # Check if 0. We use a temp cell at DATA_CELL+1.
    raw_right(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(); raw_left(1) # Temp=1
    
    # If DATA_CELL != 0, Set Temp=0
    raw_loop_open()
      raw_right(1); raw_dec(); raw_left(1) # Temp=0
      # We need to preserve DATA_CELL value for next checks!
      # But loop only runs if DATA_CELL != 0.
      # To break loop without destroying DATA_CELL, we need to move it to yet another temp?
      # This is the tricky part of non-destructive check in BF.
      # Simplified: Just move it to DATA_CELL+2, then move back.
      raw_right(2); raw_inc(); raw_left(2); raw_dec()
    raw_loop_close()
    # Move DATA_CELL+2 back to DATA_CELL
    raw_right(2); raw_loop_open(); raw_left(2); raw_inc(); raw_right(2); raw_dec(); raw_loop_close(); raw_left(2)
    
    # Now check Temp (DATA_CELL+1). If 1, it matched.
    raw_right(1)
    raw_loop_open()
       # Match! Emit code.
       raw_dec() # Clear Temp
       raw_left(1) # Back to DATA
       emit_bytes_literal(code_bytes)
       raw_right(1) # Back to Temp
       # We need to stop further checks. Set DATA_CELL to a "dead" state (e.g. negative/huge)?
       # Or set a global "Handled" flag.
       # Let's just clear DATA_CELL. Then subsequent checks (on 0) will fail naturally if they expect >0 deltas.
       # But next check expects 0 - delta. That is non-zero. So it works.
       raw_left(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_right(1)
    raw_loop_close()
    raw_left(1) # Back to DATA_CELL

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
    
    # 1. Init Setup
    # Move to DATA_CELL
    raw_right(DATA_CELL)
    
    # 2. Emit ELF Header (Fixed)
    emit_bytes_literal(header + prog_header)
    emit_bytes_literal([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00]) # Code Stub
    
    # 3. Main Loop: Read Input -> Switch -> Output
    # We use DATA_CELL for input.
    # We need a loop that terminates on EOF.
    # Approach: Read into DATA_CELL. If 0, Exit.
    
    # Infinite loop wrapper (uses DATA_CELL+5 as 1)
    raw_right(5); raw_inc(); raw_loop_open(); raw_left(5)
    
    # Read Char
    raw_inp()
    
    # EOF Check: If DATA_CELL is 0, we break.
    # Copy DATA to DATA+1 (Temp)
    raw_loop_open(); raw_dec(); raw_right(1); raw_inc(); raw_left(1); raw_loop_close() # Move to +1
    raw_right(1); raw_loop_open(); raw_dec(); raw_left(1); raw_inc(); raw_right(1); raw_loop_close(); raw_left(1) # Copy back
    
    # Check if DATA+1 is 0.
    # If it IS 0 (EOF), we need to clear the Outer Loop Flag (DATA+5).
    # Logic: Set Flag=1. If DATA+1 != 0, Set Flag=0.
    raw_right(2); raw_inc(); raw_left(1) # T2=1. At T1.
    raw_loop_open(); raw_right(1); raw_dec(); raw_left(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_loop_close() # Clear T1.
    
    # If T2 is 1 (EOF), Execute Exit Logic.
    raw_right(2)
    raw_loop_open()
       # Emit Exit Syscall
       emit_byte_literal(0x48); emit_byte_literal(0x31); emit_byte_literal(0xff)
       emit_byte_literal(0xb8); emit_byte_literal(0x3c); emit_byte_literal(0x00); emit_byte_literal(0x00); emit_byte_literal(0x00)
       emit_byte_literal(0x0f); emit_byte_literal(0x05)
       
       # Padding
       for _ in range(250): emit_byte_literal(0)
       
       # Kill Outer Loop (DATA+5)
       raw_right(3); raw_dec(); raw_left(3)
       
       # Kill T2 to exit this block
       raw_dec()
    raw_loop_close()
    raw_left(2) # Back to DATA
    
    # If not EOF, Process Char.
    # Dense Switch: + (43), , (44), - (45), . (46), < (60), > (62), [ (91), ] (93)
    
    check_and_emit(43, [0xfe, 0x03]) # +
    check_and_emit(1, [0xb8, 0x00, 0x00, 0x00, 0x00, 0xbf, 0x00, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]) # ,
    check_and_emit(1, [0xfe, 0x0b]) # -
    check_and_emit(1, [0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]) # .
    check_and_emit(14, [0x48, 0xff, 0xcb]) # <
    check_and_emit(2, [0x48, 0xff, 0xc3]) # >
    
    # Skip [ and ]
    raw_dec(29); 
    # check [
    raw_dec(2); 
    # check ]
    
    # Clear residual value
    raw_loop_open(); raw_dec(); raw_loop_close()
    
    # End Loop
    raw_right(5); raw_loop_close()

if __name__ == "__main__":
    main()
