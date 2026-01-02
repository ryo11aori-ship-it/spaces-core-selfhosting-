#!/usr/bin/env python3
# tools/gen_compiler_bf_full.py
# Level 1.7: Full Brainfuck Compiler (Interleaved Buffer + Safe Flush)
# Fix 1: Added Sentinel (255) at C99 to allow returning to C0 after flushing.
# Fix 2: Padding is now strictly enforced to exceed p_filesz to prevent truncation segfaults.

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
# C98: Wall (0)
# C99: Sentinel (255) - Marker to find way back
# C100+: Buffer [Flag, Data, Flag, Data...]

WALL_POS = 98
SENTINEL_POS = 99
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

def append_safe(vals):
    for v in vals:
        # 1. Go to Buffer Base
        right(BUFFER_BASE)
        # 2. Scan Right [>>] (Skip Flag=1)
        loop_open(); right(2); loop_close()
        # 3. Write Data
        inc() # Flag=1
        right(1)
        clear()
        if v > 0: inc(v)
        # 4. Ensure next Flag is 0
        right(1); clear()
        # 5. Return Home
        # Step back to current Flag (1)
        left(2)
        # Loop back while Flag is 1
        loop_open(); left(2); loop_close()
        # Stops at Sentinel (C99) or Wall? 
        # C99 is 255 (Non-zero). Wall C98 is 0.
        # But Buffer starts at C100.
        # The loop steps left(2).
        # Even indices: 100, 102, ... are Flags.
        # 100 -> 98. 98 is 0.
        # So it stops at C98 (Wall).
        
        # 6. Back to C0
        left(WALL_POS)
        
        # 7. Increment Total Counter C8 (Optional)
        right(8); inc(); left(8)

def check_char(char_code, logic_func):
    copy_c0_to_c1()
    right(1); dec(char_code)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(3); logic_func(); right(3); clear(); loop_close(); left(3)

def main():
    # Target File Size
    target_file_size = 500 # Valid p_filesz
    
    total_size = 1000 # Buffer padding size
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
        *p64(target_file_size), # p_filesz
        *p64(0x10000),          # p_memsz (64KB)
        *p64(0x1000)
    ]
    
    emit_bytes(header + prog_header)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])

    # Init Wall (C98=0) and Sentinel (C99=255)
    right(WALL_POS); clear(); right(); inc(255); left(SENTINEL_POS)
    
    # Init Buffer Start (C100=0)
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
    loop_open() # Loop while Flag=1
    right(1)
    out() # Emit Data
    right(1) # Move to next Flag
    loop_close()
    
    # We are now at the End of Buffer (Flag=0).
    # We need to return to C0 to allow emit_bytes to work correctly.
    # We scan LEFT looking for Sentinel (255) at C99.
    # Since Data can be anything, we must be careful.
    # But we are stepping left(2) scanning Flags.
    # Flags are 1. Wall is 0.
    # Wait, simple scan left for 0? No, wall is 0.
    # But Buffer End is 0 too.
    # We are AT Buffer End (Flag=0).
    # Step Left(2). If Flag=1, continue.
    # If Flag=0 (Wall), stop.
    
    left(2)
    loop_open(); left(2); loop_close()
    # Now at C98 (Wall).
    
    # Back to C0
    left(WALL_POS)

    # Exit Syscall
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    
    # Massive Padding to ensure FileSize > p_filesz (500)
    # Just emit 1000 zeros.
    emit_bytes([0] * 1000)

if __name__ == "__main__":
    main()
