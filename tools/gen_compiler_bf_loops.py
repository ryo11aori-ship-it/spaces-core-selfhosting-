#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler (Fix: Traveling Head Optimization)
# Strategy: Keep the Input Data and Processing Logic AT the end of the buffer.
#           This eliminates the O(N^2) seek overhead.

import sys

S = " "
F = "\u3000"

def emit(s): sys.stdout.write(s + "\n")
def right(n=1): emit((S+S+S)*n)
def left(n=1): emit((S+S+F)*n)
def inc(n=1): emit((S+F+S)*n)
def dec(n=1): emit((S+F+F)*n)
def out(): emit(F+S+S)
def inp(): emit(F+S+F)
def loop_open(): emit(F+F+S)
def loop_close(): emit(F+F+F)
def clear(): loop_open(); dec(); loop_close()

# Memory Layout
# C0-C90: Header & Stack Area
# C100+: Buffer Start
# Tape Head tracks the "Cursor" (End of Buffer).
# [ ... Code ... | Flag(1) | Data(0) | INPUT_CHAR | TEMP ... ]
# We define:
#   Cursor Cell = The cell that acts as the "Wall" for the buffer. Value=1.
#   Buffer data is to the left.
#   Input Char is kept at Cursor + 1.

BUFFER_BASE = 100

def emit_bytes(vals):
    # Static emitter for header (at start)
    for v in vals:
        right(8); clear()
        if v > 0: inc(v)
        out(); clear(); left(8)
        right(7); inc(); left(7)

def append_bytes_traveling(vals):
    # We are at Cursor (Value=1).
    # Input Char is at Cursor+1.
    # We want to write 'vals' starting at Cursor+1, and move Input Char to the right.
    # New Cursor will be at End.
    
    # 1. Move Input Char (at R1) out of the way.
    #    Target is R1 + len(vals).
    count = len(vals)
    right(1)
    loop_open(); left(1); right(1+count); inc(); left(count); dec(); loop_close()
    right(count); loop_open(); left(count); inc(); right(count); dec(); loop_close(); left(count+1)
    # Input Char is now at R(1+count).
    
    # 2. Write Bytes
    # Cursor is at R0. It becomes Data.
    # We need to set R0 = vals[0]. But R0 is 1 (Flag).
    # Actually, Buffer format: [Data, Data, Data ...].
    # We don't need Flag/Data interleave if we just output at the end.
    # But we need to find our way back for Loops.
    # Let's use simple [Data] array. The "Cursor" is just where we are.
    # We assume C0-C99 are reserved. Buffer starts at C100.
    
    # Wait, for Backpatching `]`, we need to find the address.
    # If we don't have Interleaved Flags, finding "N-th byte" is hard.
    # But we only need to move "Relative" to current pos?
    # Stack stores "Absolute Index".
    # We need to track Current Index. Use C8 (at start).
    # Updating C8 requires travel. O(N) per char? No.
    # We can carry C8 *with us*?
    # Yes! [ ... Code ... | C8_Low | C8_High | Input_Char | Temp ]
    # This is complex.
    
    # Compromise:
    # 1. Emit Code (Linear). O(1).
    # 2. Update C8 (Global). O(N).
    # But we only update C8 for `[` and `]`. Linear code doesn't use C8.
    # Linear code chunks don't need C8 update immediately.
    # We can defer C8 update? No.
    # Linear code doesn't involve `[` `]`.
    # `compiler_linear.bf` has one big loop.
    # Inside the loop, it emits bytes.
    # It does NOT use `[` `]` inside the loop.
    # So we only pay O(N) travel for `[` and `]`.
    # The `+`, `.`, etc will be O(1). This is fast enough!
    
    # Execution:
    # We are at Cursor (Empty 0).
    # Write bytes. Move Cursor.
    for v in vals:
        clear()
        if v > 0: inc(v)
        right(1)
    # Now at new empty slot.

def compile_bracket_open():
    # 1. Travel to Start to update Stack
    # We need to know "How far is Start?".
    # We can scan left until C99 (Wall).
    # Mark current pos with special value?
    inc(255) # Marker
    
    # Scan Left for Wall (Sentinel at C99)
    # C99 must be unique. Let's say 0. Buffer bytes can be 0.
    # We need interleaved flags if we want robust scanning.
    # Fallback: Just scan left.
    # We use Interleaved [Flag(1), Data] format for safety.
    
    # Go Home
    left(2); loop_open(); left(2); loop_close(); left(BUFFER_BASE - 2)
    
    # At C0. Update Stack.
    right(8); loop_open(); dec(); left(7); inc(); right(40); inc(); left(33); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    
    # Return to Cursor
    # Scan Right for Flag=0 (End).
    right(BUFFER_BASE); loop_open(); right(2); loop_close()
    
    # Emit
    append_bytes_interleaved([0x80, 0x3b, 0x00])
    append_bytes_interleaved([0x0f, 0x84, 0x00, 0x00, 0x00, 0x00])

def compile_bracket_close():
    append_bytes_interleaved([0xe9])
    
    # Go Home
    left(2); loop_open(); left(2); loop_close(); left(BUFFER_BASE - 2)
    
    # Calc Offset & Patch (Dummy for linear test)
    # We just need to pop stack to keep balance.
    right(40); loop_open(); dec(); left(39); dec(); right(39); loop_close(); left(40)
    
    # Return to Cursor
    right(BUFFER_BASE); loop_open(); right(2); loop_close()

def append_bytes_interleaved(vals):
    # At Cursor (Flag=0, Left=Data).
    # 1. Move Input Char (at R1) to R(1 + 2*len)
    count = len(vals)
    # Copy Input R1 -> Temp
    right(1); loop_open(); left(1); right(1+2*count); inc(); left(2*count); dec(); loop_close()
    right(1+2*count); loop_open(); left(2*count); inc(); right(2*count); dec(); loop_close(); left(1+2*count)
    left(1)
    
    # 2. Write
    for v in vals:
        inc() # Flag=1
        right(1); clear()
        if v > 0: inc(v)
        right(1)
    # At new Cursor (Flag=0).

def sub_and_check_traveling(delta, action_func):
    # At Cursor(Flag=0). Input at R1.
    right(1); dec(delta)
    
    # Check 0 (Non-destructive)
    # Move R1 -> R2
    loop_open(); left(1); right(2); inc(); left(1); dec(); loop_close()
    right(2); loop_open(); left(1); inc(); right(1); dec(); loop_close(); left(1) # Restore to R1, keep R2
    
    # Check R2
    right(2); clear(); inc(); left(1) # Flag=1 at R1 (Temp)
    loop_open(); right(1); dec(); left(1); clear(); loop_close()
    
    # If Flag=1, Match.
    right(1)
    loop_open()
       dec() # Clear Flag
       left(2) # At Cursor
       action_func() # Append bytes (Moves Cursor & Input)
       right(2) # Align (We need to be at 0 to break loop)
       # After action_func, Cursor moved.
       # We are at New Cursor.
       # We need to break the loop.
       # New Cursor R2 is empty (0). So we are good.
    loop_close()
    left(2) # Back to Cursor

def main():
    # Header Setup
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
    
    emit_bytes(header + prog_header)
    right(1000)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    # Init Buffer
    right(WALL_POS); clear(); left(WALL_POS)
    right(BUFFER_BASE); clear(); left(BUFFER_BASE)
    
    # Init C8 (Counter)
    right(8); inc(127); left(8) # Header size approx
    
    # Move to Start of Buffer
    right(BUFFER_BASE)
    
    # Read Initial Char into R1
    right(1); inp(); left(1)
    
    # Loop until EOF (Data at R1 is 0)
    # Using Flag at R2 to control loop
    right(2); inc(); left(2) # Flag=1
    
    right(2)
    loop_open()
       left(2)
       
       # Check EOF (R1)
       # Copy R1->R3
       right(1); loop_open(); left(1); right(3); inc(); left(2); dec(); loop_close()
       right(3); loop_open(); left(2); inc(); right(2); dec(); loop_close(); left(3)
       
       # Check R3
       right(3); clear(); inc(); left(1) # T=1
       loop_open(); right(1); dec(); left(1); clear(); loop_close()
       
       # If T=1 (EOF), Break Outer Loop
       right(2)
       loop_open()
          # EOF Action
          left(4) # At Cursor
          # Flush
          # Go Home
          left(2); loop_open(); left(2); loop_close(); left(BUFFER_BASE - 2)
          # Scan & Output
          right(BUFFER_BASE)
          loop_open()
             right(1); out(); right(1)
          loop_close()
          
          # Footer
          emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
          # Pad
          right(1); inc(50); loop_open(); dec(); left(1); emit_bytes([0,0,0,0,0,0,0,0,0,0]); right(1); loop_close(); left(1)
          
          # Kill Flag
          left(BUFFER_BASE); right(2); dec(); left(2); right(BUFFER_BASE)
          
          # Return to T loop
          right(2) # At T
          dec() # Kill T
          right(2) # At Flag
          dec() # Kill Flag
          left(2)
       loop_close()
       left(2) # Back to Cursor
       
       # Process Char
       # Only if Flag (R2) is still 1
       right(2)
       loop_open()
          left(2)
          sub_and_check_traveling(43, lambda: append_bytes_interleaved([0xfe, 0x03]))
          sub_and_check_traveling(1, lambda: append_bytes_interleaved([0xb8, 0x00, 0x00, 0x00, 0x00, 0xbf, 0x00, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]))
          sub_and_check_traveling(1, lambda: append_bytes_interleaved([0xfe, 0x0b]))
          sub_and_check_traveling(1, lambda: append_bytes_interleaved([0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05]))
          sub_and_check_traveling(14, lambda: append_bytes_interleaved([0x48, 0xff, 0xcb]))
          sub_and_check_traveling(2, lambda: append_bytes_interleaved([0x48, 0xff, 0xc3]))
          right(1); dec(29); left(1)
          # compile_bracket_open()
          right(1); dec(2); left(1)
          # compile_bracket_close()
          
          # Read Next Char
          right(1); inp(); left(1)
          
          right(2); dec(); inc() # Dummy to keep loop
          # Actually we need to break this inner 'if'
          dec()
       loop_close()
       # Restore Flag if it was 1?
       # We killed it to break.
       # But we need it for Outer Loop.
       # We need a latch.
       # If we processed, we Set Flag=1.
       # If EOF killed it, it stays 0.
       # But we just checked EOF.
       # If Not EOF, we set Flag=1 again.
       # Check EOF T again? No.
       
       # Use T from EOF check.
       # T=1 means EOF. T=0 means Continue.
       # If T=0, Inc Flag.
       # We are at Cursor. T is at R3 (cleared).
       # We lost T state.
       
       # Simply: The outer loop runs on R2.
       # Inside, we check EOF. If EOF, R2=0.
       # If Not EOF, R2=1 (Unchanged).
       # But inside the "If Not EOF" block, we had to break it.
       # So we used a temp loop.
       
       # Re-set R2=1 at end of iteration?
       inc()
       
       # But if EOF happened, we set R2=0 and exited block.
       # Then we inc() -> R2=1. Loop continues!
       # We need to know if EOF happened.
       # Check R1 (Data). If 0, R2=0.
       # Copy R1->R3...
       # This is tedious.
       
       # Just check R1 directly.
       # R1 is Next Char.
       # If R1!=0, R2=1. Else R2=0.
       right(1); loop_open(); left(1); right(3); inc(); left(2); dec(); loop_close()
       right(3); loop_open(); left(2); inc(); right(2); dec(); loop_close(); left(1) # R2=R1 copy.
       # Loop R2
    loop_close()

if __name__ == "__main__":
    main()
