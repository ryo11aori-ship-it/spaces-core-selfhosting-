#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py
# Level 1.9: Full BF Compiler (Optimization: Head-at-End & Indentation Safe)

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
# C98: Wall (0)
# C100+: Interleaved Buffer [Flag, Data]
# Flag: 1=Filled, 2=Cursor

WALL_POS = 98
BUFFER_BASE = 100

def emit_bytes(vals):
    for v in vals:
        right(8); clear()
        if v > 0: inc(v)
        out(); clear(); left(8)
        right(7); inc(); left(7)

def stream_bytes(vals):
    # Assumes Cursor is at Flag=2.
    first = True
    for v in vals:
        if not first:
            right(2)
        clear(); inc()
        right(1); clear()
        if v > 0: inc(v)
        left(1)
        first = False
    right(2); clear(); inc(2)

def go_home_from_cursor():
    left(2)
    loop_open(); left(2); loop_close()
    left(WALL_POS)

def return_to_cursor():
    right(WALL_POS)
    loop_open()
    dec()
    right(1); inc(); left(1)
    loop_open()
    right(1); dec(); left(1)
    inc()
    loop_open(); left(1); loop_close()
    right(1)
    loop_close()
    left(1)
    right(1)
    loop_open()
    dec()
    left(1); inc(); right(2)
    inc()
    loop_close()
    left(1)
    loop_close()

def compile_bracket_open():
    go_home_from_cursor()
    right(8); loop_open(); dec(); left(7); inc(); right(40); inc(); left(33); loop_close()
    right(1); loop_open(); dec(); left(1); inc(); right(1); loop_close(); left(1)
    return_to_cursor()
    stream_bytes([0x80, 0x3b, 0x00])
    stream_bytes([0x0f, 0x84, 0x00, 0x00, 0x00, 0x00])

def compile_bracket_close():
    stream_bytes([0xe9])
    go_home_from_cursor()
    return_to_cursor()

def check_char_streaming(char_code, bytes_to_emit):
    right(1); dec(char_code)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); dec(); left(2); clear(); loop_close()
    right(2)
    loop_open()
    dec()
    left(3)
    stream_bytes(bytes_to_emit)
    right(3)
    loop_close()
    left(3)

def pad_zeros(count):
    # Runtime padding
    right(1); clear(); inc(count // 10)
    loop_open()
    dec(); left(1)
    for _ in range(10):
        right(8); clear(); out(); clear(); left(8)
        right(7); inc(); left(7)
    right(1)
    loop_close()
    left(1)

def main():
    target_file_size = 500
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
        *p64(target_file_size), *p64(0x10000), *p64(0x1000)
    ]
    
    emit_bytes(header + prog_header)
    right(1000)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    
    right(WALL_POS); clear(); left(WALL_POS)
    right(BUFFER_BASE); clear(); inc(2); left(BUFFER_BASE)
    
    # Outer Loop (Infinite until EOF breaks)
    # We use C90=1 as 'Running' flag.
    left(BUFFER_BASE); right(90); inc(); loop_open()
    right(10) # To Buffer Base
    return_to_cursor()
    
    # Read Input
    right(1); inp()
    
    # Check EOF (Data!=0)
    loop_open()
    # Not EOF, Process
    loop_open(); left(1); inc(); right(2); inc(); left(1); dec(); loop_close()
    right(2); loop_open(); left(2); inc(); right(2); dec(); loop_close(); left(1)
    
    check_char_streaming(62, [0x48, 0xff, 0xc3])
    check_char_streaming(60, [0x48, 0xff, 0xcb])
    check_char_streaming(43, [0xfe, 0x03])
    check_char_streaming(45, [0xfe, 0x0b])
    check_char_streaming(46, [0xb8, 0x01, 0x00, 0x00, 0x00, 0xbf, 0x01, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    check_char_streaming(44, [0xb8, 0x00, 0x00, 0x00, 0x00, 0xbf, 0x00, 0x00, 0x00, 0x00, 0x48, 0x89, 0xde, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05])
    
    compile_bracket_open() 
    compile_bracket_close()
    
    clear() # Clear Data
    left(1); inc(3); right(1) # Set Flag=3 (Temp Not-EOF)
    loop_close()
    
    # Back at Flag
    # If Flag=2, it was EOF (Loop didn't run).
    # If Flag=3, it was Not EOF.
    
    left(1) # At Flag
    # Dec 2. If 0 -> EOF.
    dec(); dec()
    # Check 0
    right(1); inc(); left(1) # Temp C_Chk=1
    loop_open()
    right(1); dec(); left(1) # C_Chk=0
    inc(); inc() # Restore Flag=2 (actually 2 for next iter cursor)
    loop_open(); left(1); loop_close() # Clear loop var
    loop_close()
    
    right(1)
    # If C_Chk=1 (EOF), Flush and Exit.
    loop_open()
    # Go Home
    left(1) # Back to Flag=0 (was 2)
    # We destroyed the cursor logic by dec(2).
    # But we are exiting.
    # Restore Flag=2 for flush logic scan?
    # Flush scans for 1. Stops at 2.
    # Previous are 1.
    # Current is 0.
    inc(2) # Restore 2
    go_home_from_cursor()
    
    # Flush
    right(BUFFER_BASE)
    loop_open()
    right(1); out(); right(1)
    loop_close()
    
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    pad_zeros(500)
    
    # Trap (Infinite Loop to satisfy VM until timeout kills it, saving output)
    loop_open(); loop_close()
    
    loop_close() # End if
    
    # If Not EOF, Flag is 1 (was 3, dec 2 = 1).
    # We need it to be 2 for next cursor?
    # No, `stream_bytes` makes new cursor 2.
    # The current cell is the *OLD* cursor, which is now filled (1).
    # So 1 is correct!
    
    left(1) # At Flag=1
    # We are deep in buffer.
    # We need to loop outer.
    # But outer loop checks C90.
    # We can't go back to C90 easily every char (O(N^2)).
    # So we loop INFINITELY here?
    # No, `loop_open` at start corresponds to `left(BUFFER_BASE); ... loop_close()`.
    # That loop expects us to be at C90.
    # We are at C_Deep.
    # THIS IS THE PROBLEM with O(N) logic in BF.
    # We cannot return to C90 efficiently.
    
    # Solution: The Outer Loop is `[ ... ]` (Infinite).
    # Inside, we perform logic.
    # If EOF, we Trap.
    # If Not EOF, we just... continue?
    # But where is the loop jump back to?
    # The `]` jumps back to `[`.
    # The `[` checks the cell value.
    # The cell must be non-zero.
    # We are at Flag=1.
    # If we put `]` here, it jumps back to `[`?
    # No, `[` is at C90.
    # `]` expects us to be at C90.
    # If we are at C_Deep, `]` checks C_Deep!=0, jumps back to matching `[`.
    # Matching `[` is at C90.
    # Jump offset is calculated at compile time.
    # Dynamic tape position is runtime.
    # BF doesn't care where tape head is, `]` just jumps in code.
    # So `]` jumps to code start.
    # Code start executes `right(10); return_to_cursor()`.
    # This expects us to be at C90!
    # If we are at C_Deep, `right(10)` goes to C_Deep+10.
    # `return_to_cursor` fails.
    
    # WE MUST GO HOME every char.
    # Is it O(N^2)?
    # `go_home` is `left` until Wall.
    # Distance is proportional to output size.
    # Input size M. Output size N.
    # Total steps: 1+2+3...N = O(N^2).
    # 5KB file -> 5000^2 steps = 25,000,000 steps.
    # VM speed is fast. 25M steps is ~1 second.
    # So O(N^2) IS ACCEPTABLE for 5KB file!
    # The timeout earlier was likely due to Python script generating too much logic per char, or inefficiency.
    
    # So `go_home` is fine.
    
    go_home_from_cursor()
    left(10) # Back to C90
    loop_close() # Loop C90

if __name__ == "__main__":
    main()
