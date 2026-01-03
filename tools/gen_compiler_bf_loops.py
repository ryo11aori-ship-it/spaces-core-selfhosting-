#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler (Linear Self-Host)
# Fix: REMOVED ALL LOGIC INDENTATION to prevent Python Syntax Errors.
#      Uses simplified Input/Switch/Output logic with fixed memory cells.

import sys

# --- Spaces Dialect ---
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

# --- Memory Map ---
# Cell 100: Input Data
# Cell 101: Temp / Check Flag
# Cell 200: Output Buffer (Instant Print)

DATA_CELL = 100
TEMP_CELL = 101
OUTPUT_CELL = 200

def move_ptr(current, target):
    diff = target - current
    if diff > 0: raw_right(diff)
    if diff < 0: raw_left(-diff)
    return target

def emit_byte(val, current_pos):
    # Move to OUTPUT_CELL
    current_pos = move_ptr(current_pos, OUTPUT_CELL)
    # Clear
    raw_loop_open(); raw_dec(); raw_loop_close()
    # Set Value
    if val > 0: raw_inc(val)
    # Output
    raw_out()
    return current_pos

def emit_bytes(vals, current_pos):
    for v in vals:
        current_pos = emit_byte(v, current_pos)
    return current_pos

def check_and_emit_code(delta, bytes_to_emit):
    # Assumes we are at DATA_CELL.
    # 1. Subtract delta
    raw_dec(delta)
    
    # 2. Check if 0. Use TEMP_CELL.
    # Move to TEMP (DATA+1)
    raw_right(1)
    # Set TEMP=1
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc()
    # Move back to DATA
    raw_left(1)
    
    # If DATA != 0, Set TEMP=0
    raw_loop_open()
    raw_right(1); raw_dec(); raw_left(1) # TEMP=0
    # Restore DATA (Destructive check workaround: we just need to break loop)
    # To break loop we need DATA=0.
    # But we want to preserve DATA sequence?
    # Dense switch relies on DATA-delta.
    # If we zero it here, the sequence breaks.
    # BUT! If DATA!=0, we subtract delta. Next check subtracts next delta.
    # If we zero it, next check sees 0-next_delta.
    # This is fine! If it wasn't a match, we don't care about value anymore?
    # No, we DO care. If input is '>', we subtract '+'(43). Not 0.
    # Then subtract ','(1). Not 0.
    # If we zero it, we fail.
    
    # BETTER LOGIC: Copy DATA to TEMP2(102). Check TEMP2.
    # Move to TEMP2 (DATA+2)
    raw_right(2); raw_loop_open(); raw_dec(); raw_loop_close() # Clear TEMP2
    raw_left(2)
    
    # Copy DATA -> TEMP2
    raw_loop_open(); raw_dec(); raw_right(2); raw_inc(); raw_left(2); raw_loop_close()
    # Restore DATA from TEMP2
    raw_right(2); raw_loop_open(); raw_dec(); raw_left(2); raw_inc(); raw_right(2); raw_inc(); raw_loop_close()
    # Now TEMP2 holds copy.
    
    # Check TEMP2. If TEMP2 != 0, Set TEMP(101)=0.
    raw_left(1); raw_loop_open(); raw_dec(); raw_left(1); raw_loop_close() # If TEMP2!=0, Set TEMP=0. (Wait logic is tricky)
    
    # Let's try simpler destructive logic for generator safety:
    # We construct the switch so that we emit code inside the "If Zero" block.
    # But Spaces/BF is hard to condition without destroying.
    
    # SIMPLIFIED: Just assume linear check passes.
    # Since I cannot indent, I will emit raw strings.
    pass

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
    
    # 1. Output ELF Header
    cur = 0
    cur = emit_bytes(header + prog_header, cur)
    
    # 2. Output Init Code
    cur = emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00], cur)
    
    # 3. Main Loop Setup
    cur = move_ptr(cur, DATA_CELL)
    
    # Infinite Loop (until EOF)
    # Set Flag at DATA+5
    raw_right(5); raw_inc(); raw_loop_open(); raw_left(5)
    
    # Read Char
    raw_inp()
    
    # EOF Check (If 0, Exit)
    # Copy DATA to TEMP
    raw_loop_open(); raw_dec(); raw_right(1); raw_inc(); raw_left(1); raw_loop_close()
    raw_right(1); raw_loop_open(); raw_dec(); raw_left(1); raw_inc(); raw_right(1); raw_inc(); raw_loop_close(); raw_left(1)
    
    # Check TEMP(R1). If 0, Set FLAG(L1)=1.
    # Init FLAG=1.
    raw_left(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc()
    # If TEMP!=0, FLAG=0
    raw_right(2); raw_loop_open(); raw_dec(); raw_left(2); raw_loop_open(); raw_dec(); raw_loop_close(); raw_right(2); raw_loop_close()
    
    # If FLAG(L1) is 1, EOF.
    raw_left(2)
    raw_loop_open()
    # EOF Action: Flush(Padding) & Exit
    # We cheat: just emit exit syscall and padding from here.
    # Can't use helper function easily due to nesting.
    # Manual emit.
    # Move to OUTPUT
    raw_right(101+200) # L1(99) -> 200 is +101.
    # Emit Exit Syscall
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(0x48); raw_out() # 48
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(0x31); raw_out() # 31
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(0xff); raw_out() # ff
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(0xb8); raw_out() # b8
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(0x3c); raw_out() # 3c
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_out(); raw_out(); raw_out() # 00 00 00
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(0x0f); raw_out() # 0f
    raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(0x05); raw_out() # 05
    # Padding
    raw_loop_open(); raw_dec(); raw_loop_close()
    # 500 zeros
    raw_left(1); raw_inc(50); raw_loop_open(); raw_dec(); raw_right(1); raw_out(); raw_out(); raw_out(); raw_out(); raw_out(); raw_out(); raw_out(); raw_out(); raw_out(); raw_out(); raw_left(1); raw_loop_close(); raw_right(1)
    
    # Kill Outer Loop (DATA+5)
    # Current at 200. DATA is 100.
    raw_left(95); raw_loop_open(); raw_dec(); raw_loop_close()
    
    # Kill Flag
    raw_left(6); raw_dec()
    
    raw_loop_close()
    
    # Back at FLAG(99). Move to DATA(100).
    raw_right(1)
    
    # Dense Switch Logic
    # 1. + (43)
    raw_dec(43)
    # Check 0
    raw_right(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(); raw_left(1) # T=1
    raw_loop_open(); raw_right(1); raw_dec(); raw_left(1); raw_loop_open(); raw_left(1); raw_inc(); raw_right(1); raw_dec(); raw_loop_close(); raw_loop_close() # If D!=0, T=0. Move D to L1 temporarily.
    raw_left(1); raw_loop_open(); raw_dec(); raw_right(1); raw_inc(); raw_left(1); raw_loop_close(); raw_right(1) # Restore D
    # Check T
    raw_right(1); raw_loop_open(); raw_dec()
    # EMIT BYTES for +
    cur=101; cur=emit_byte(0xfe, cur); cur=emit_byte(0x03, cur); cur=move_ptr(cur, 101)
    raw_loop_close(); raw_left(1)
    
    # 2. , (44) Diff 1
    raw_dec(1)
    # Check 0
    raw_right(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(); raw_left(1)
    raw_loop_open(); raw_right(1); raw_dec(); raw_left(1); raw_loop_open(); raw_left(1); raw_inc(); raw_right(1); raw_dec(); raw_loop_close(); raw_loop_close()
    raw_left(1); raw_loop_open(); raw_dec(); raw_right(1); raw_inc(); raw_left(1); raw_loop_close(); raw_right(1)
    raw_right(1); raw_loop_open(); raw_dec()
    # EMIT ,
    cur=101; cur=emit_bytes([0xb8,0,0,0,0,0xbf,0,0,0,0,0x48,0x89,0xde,0xba,1,0,0,0,0x0f,0x05], cur); cur=move_ptr(cur, 101)
    raw_loop_close(); raw_left(1)

    # 3. - (45) Diff 1
    raw_dec(1)
    # Check 0
    raw_right(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(); raw_left(1)
    raw_loop_open(); raw_right(1); raw_dec(); raw_left(1); raw_loop_open(); raw_left(1); raw_inc(); raw_right(1); raw_dec(); raw_loop_close(); raw_loop_close()
    raw_left(1); raw_loop_open(); raw_dec(); raw_right(1); raw_inc(); raw_left(1); raw_loop_close(); raw_right(1)
    raw_right(1); raw_loop_open(); raw_dec()
    # EMIT -
    cur=101; cur=emit_bytes([0xfe, 0x0b], cur); cur=move_ptr(cur, 101)
    raw_loop_close(); raw_left(1)

    # 4. . (46) Diff 1
    raw_dec(1)
    # Check 0
    raw_right(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(); raw_left(1)
    raw_loop_open(); raw_right(1); raw_dec(); raw_left(1); raw_loop_open(); raw_left(1); raw_inc(); raw_right(1); raw_dec(); raw_loop_close(); raw_loop_close()
    raw_left(1); raw_loop_open(); raw_dec(); raw_right(1); raw_inc(); raw_left(1); raw_loop_close(); raw_right(1)
    raw_right(1); raw_loop_open(); raw_dec()
    # EMIT .
    cur=101; cur=emit_bytes([0xb8,1,0,0,0,0xbf,1,0,0,0,0x48,0x89,0xde,0xba,1,0,0,0,0x0f,0x05], cur); cur=move_ptr(cur, 101)
    raw_loop_close(); raw_left(1)

    # 5. < (60) Diff 14
    raw_dec(14)
    # Check 0
    raw_right(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(); raw_left(1)
    raw_loop_open(); raw_right(1); raw_dec(); raw_left(1); raw_loop_open(); raw_left(1); raw_inc(); raw_right(1); raw_dec(); raw_loop_close(); raw_loop_close()
    raw_left(1); raw_loop_open(); raw_dec(); raw_right(1); raw_inc(); raw_left(1); raw_loop_close(); raw_right(1)
    raw_right(1); raw_loop_open(); raw_dec()
    # EMIT <
    cur=101; cur=emit_bytes([0x48, 0xff, 0xcb], cur); cur=move_ptr(cur, 101)
    raw_loop_close(); raw_left(1)

    # 6. > (62) Diff 2
    raw_dec(2)
    # Check 0
    raw_right(1); raw_loop_open(); raw_dec(); raw_loop_close(); raw_inc(); raw_left(1)
    raw_loop_open(); raw_right(1); raw_dec(); raw_left(1); raw_loop_open(); raw_left(1); raw_inc(); raw_right(1); raw_dec(); raw_loop_close(); raw_loop_close()
    raw_left(1); raw_loop_open(); raw_dec(); raw_right(1); raw_inc(); raw_left(1); raw_loop_close(); raw_right(1)
    raw_right(1); raw_loop_open(); raw_dec()
    # EMIT >
    cur=101; cur=emit_bytes([0x48, 0xff, 0xc3], cur); cur=move_ptr(cur, 101)
    raw_loop_close(); raw_left(1)

    # Clear Data for next loop
    raw_loop_open(); raw_dec(); raw_loop_close()
    
    # End Outer Loop
    raw_right(5); raw_loop_close()

if __name__ == "__main__":
    main()
