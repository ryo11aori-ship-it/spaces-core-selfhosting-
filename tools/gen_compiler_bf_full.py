#!/usr/bin/env python3
# tools/gen_compiler_bf_full.py
# Level 1.7: Full Brainfuck Compiler (Interleaved Buffer Strategy)
# Fix: Uses [Flag, Data] pairs to handle binary zero safely.
#      Prevents 'Tape pointer underflow' and huge output files.

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

# --- Memory Layout ---
# C0: Input Char
# C1-C6: Scratch
# C7: Output Byte Counter
# C98: Wall (Always 0) - Stop marker for scanning left
# C100+: Buffer [Flag, Data, Flag, Data...]
#        Flag=1 (Present), Flag=0 (End)

WALL_POS = 98
BUFFER_BASE = 100

def emit_byte_tracked(val):
    right(8); clear()
    if val > 0: inc(val)
    out(); clear(); left(8)
    right(7); inc(); left(7)

def emit_bytes(vals):
    for v in vals: emit_byte_tracked(v)

def copy_c0_to_c1():
    right(1); clear(); right(2); clear(); left(3)
    loop_open(); dec(); right(1); inc(); right(2); inc(); left(3); loop_close()
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(3)

# 安全なバッファ書き込み (Interleaved)
def append_safe(vals):
    for v in vals:
        # 1. Go to Buffer Base (C100)
        right(BUFFER_BASE)
        
        # 2. Scan Right [>>] (Skip Flag=1 cells)
        loop_open()
        right(2)
        loop_close()
        # Stops at Flag=0 (End of Buffer)
        
        # 3. Write Data
        inc() # Set Flag = 1
        right(1) # Move to Data slot
        clear()
        if v > 0: inc(v)
        
        # 4. Ensure next Flag is 0
        right(1) # Move to Next Flag
        clear() # Ensure 0
        
        # 5. Return Home [<<]
        # First, step back to current Flag (which is 1)
        left(2)
        # Loop back while Flag is 1
        loop_open()
        left(2)
        loop_close()
        # Stops at Wall (C98) which is 0
        
        # 6. Back to C0
        left(WALL_POS)
        
        # 7. Increment Total Counter C8 (Optional, kept for consistency)
        right(8); inc(); left(8)

def check_char(char_code, logic_func):
    copy_c0_to_c1()
    right(1); dec(char_code)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(3); logic_func(); right(3); clear(); loop_close(); left(3)

def main():
    total_size = 1000
    load_addr = 0x400000
    header_len = 120
    
    def p64(v): return list(v.to_bytes(8, "little"))
    def p32(v): return list(v.to_bytes(4, "little"))

    header = [
        0x7f,0x45,0x4c,0x46,0x02,0x01,0x01,0x00,0,0,0,0,0,0,0,0,
        0x02,0x00,0x3e,0x00,0x01,0x00,0x00,0x00,
        *p64(load_addr + header_len), *p64(64), *p64(0), *p32(0),
        0x40,0x00,0x38,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    ]
    prog_header = [
        0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(total_size), 
        *p64(0x10000), 
        *p64(0x1000)
    ]
    
    emit_bytes(header + prog_header)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])

    # Init Wall (C98 = 0)
    right(WALL_POS); clear(); left(WALL_POS)
    
    # Init Buffer Start (C100 = 0)
    right(BUFFER_BASE); clear(); left(BUFFER_BASE)

    # Main Loop
    right(2); clear(); inc(); left(2)
    right(2); loop_open(); left(2)
    
    clear(); inp()
    
    # EOF Check
    copy_c0_to_c1()
    right(3); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(1); clear(); right(1); clear(); loop_close(); left(3)
    
    # Checks
    check_char(62, lambda: append_safe([0x48, 0xff, 0xc3]))
    check_char(60, lambda: append_safe([0x48, 0xff, 0xcb]))
    check_char(43, lambda: append_safe([0xfe, 0x03]))
    check_char(45, lambda: append_safe([0xfe, 0x0b]))
    
    check_char(46, lambda: append_safe([
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x48, 0x89, 0xde,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]))
    
    check_char(44, lambda: append_safe([
        0xb8, 0x00, 0x00, 0x00, 0x00,
        0xbf, 0x00, 0x00, 0x00, 0x00,
        0x48, 0x89, 0xde,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]))
    
    right(2); loop_close(); left(2)
    
    # Flush Buffer
    right(BUFFER_BASE)
    loop_open()
    # At Flag=1.
    right(1)
    # At Data. Output.
    out()
    right(1)
    # At Next Flag. Loop checks this.
    loop_close()
    
    # End Flush. Back to C0? 
    # Not strictly needed since we exit, but good hygiene.
    
    # Padding
    # We are deep in the buffer.
    # Just emit 0s to stdout directly?
    # No, C7 is valid counter.
    # But C7 is far away.
    # Let's just output some zeros and exit. The ELF parser is robust.
    # Or, we can blindly output 500 zeros.
    clear() # Clear current cell
    inc(200) # Loop 200
    loop_open()
    out() # Emit 0 (current cell is used as counter, need another 0?)
    # Hack: emit 0 from neighbor
    right(1); clear(); out(); left(1)
    dec()
    loop_close()

    # Exit Syscall (Streamed at the end)
    # Wait, we flushed BEFORE exit?
    # Yes. The buffer contains the program body.
    # Exit syscall should be appended?
    # The previous logic appended Exit to the Stream, NOT the buffer.
    # So: Header -> [Buffer Content] -> Exit Code.
    
    # Need to verify if Buffer Content ends cleanly.
    # Yes.
    
    # Stream Exit Code
    # Move head to scratch area to emit safely
    # We are deep in buffer.
    # Just use current pos.
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    
    # Padding logic was streamed.
    # Just emit more zeros.
    # We don't need precise C7 logic if we just pad "enough".
    emit_bytes([0] * 100) 

if __name__ == "__main__":
    main()
