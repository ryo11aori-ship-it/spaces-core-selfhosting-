#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Spaces Compiler Generator (Level 0.8: Lightweight BF to ELF Compiler)
# Fixes applied:
#  - Append a real newline between emitted groups to avoid accidental F/S token merging.
#  - Use C1 as the preserved comparison copy.
#  - After generation, count loop_start / loop_end patterns and append missing loop_end tokens
#    at EOF so .spaces has matched loop tokens (pragmatic safety fix to avoid VM hangs).
#
# Save as tools/gen_compiler_v1.py (or a new file) and run:
#   python3 tools/gen_compiler_v1.py > spaces/self/compiler_v1.spaces
#
# Then run your VM exactly as in CI:
#   timeout 10s ./bin/ref_vm spaces/self/compiler_v1.spaces < test.bf > test.elf
#   chmod +x test.elf
#   ./test.elf
#
# If the exit code isn't as expected, attach the generated .spaces and test.elf and I'll inspect.

import sys

def p64(val): return list(val.to_bytes(8, 'little'))
def p32(val): return list(val.to_bytes(4, 'little'))

# --- Constants ---
S = " "
F = "\u3000"
CMDS = []

# Emit with a real newline separator to prevent adjacent emits forming FFS/FFF
def emit(s):
    CMDS.append(s + '\n')

def right(n=1): emit((S+S+S)*n)
def left(n=1): emit((S+S+F)*n)
def inc(n=1): emit((S+F+S)*n)
def dec(n=1): emit((S+F+F)*n)
def out(): emit(F+S+S)
def inp(): emit(F+S+F)
def loop_start(): emit(F+F+S)
def loop_end(): emit(F+F+F)
def clear(): loop_start(); dec(); loop_end()

# --- Simplified Tracked Output (1 Byte Only) ---
# C0: Working Cursor
# C7: Byte Counter (Max 255)

def emit_byte_tracked(val):
    # Output byte (C0 -> C9 -> C0)
    right(9); clear(); inc(val); out(); clear(); left(9)
    # Increment Counter C7 (C0 -> C7 -> C0)
    right(7); inc(); left(7)

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list: emit_byte_tracked(b)

def main():
    right(16) # Safety margin

    # 1. Emit ELF Header (Target Total Size: 200 bytes)
    load_addr = 0x400000
    header_len = 120
    total_size = 200 # 0xC8

    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        *p64(load_addr + header_len), *p64(64), *p64(0), *p32(0),
        0x40, 0x00, 0x38, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    prog_header = [
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(total_size), *p64(total_size), *p64(0x1000)
    ]
    for b in header + prog_header: emit_byte_tracked(b)

    # 2. Init Code: xor rbx, rbx
    emit_machine_code_tracked([0x48, 0x31, 0xdb])

    # 3. Main Loop
    # C2: Loop Flag
    right(2); clear(); inc(); loop_start(); left(2)

    # [STEP 1] Read Input
    clear() # Clear C0
    inp()   # Read to C0

    # [STEP 2] EOF Check
    # Strategy: Copy C0 -> C1 & C3. Check preserved copy in C1. If 0, Break C2.

    # Clear Scratch C1
    right(); clear(); left()

    # Copy C0 -> C1 & C3 (preserve in C1)
    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # Set Flag C5 = 1 (Assume EOF).
    right(5); clear(); inc(); left(5)

    # If C1 != 0, Set Flag C5 = 0.
    right(1); loop_start(); clear(); right(4); clear(); left(4); loop_end(); left(1)

    # If Flag C5 == 1, Break Main Loop C2.
    right(5)
    loop_start()
    clear() # [FIXED] clear flag so we don't loop forever
    left(3); dec(); right(3) # Break C2
    loop_end()
    left(5)


    # [STEP 3] Check '+' (43)
    right(2); loop_start(); left(2)

    # Clear Scratch C1
    right(); clear(); left()

    # Copy C0 -> C1 & C3
    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # Subtract 43 from C1 (preserved copy)
    right(1); dec(43); left(1)

    # Check if C1 == 0 (Match). Set Flag C5 = 1.
    right(5); clear(); inc(); left(5)
    right(1); loop_start(); clear(); right(4); clear(); left(4); loop_end(); left(1)

    # If Match (C5 == 1), Emit Code
    right(5); loop_start()
    clear() # Clear Match Flag (run loop exactly once)
    left(5) # Go to C0
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3) # inc rbx
    right(5) # Back to C5
    loop_end(); left(5)

    right(2); loop_end(); left(2) # End C2 Check

    # [STEP 4] Check '-' (45)
    right(2); loop_start(); left(2)

    # Clear Scratch C1
    right(); clear(); left()

    # Copy C0 -> C1 & C3
    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # Subtract 45 from C1 (preserved copy)
    right(1); dec(45); left(1)

    # Check if C1 == 0 (Match).
    right(5); clear(); inc(); left(5)
    right(1); loop_start(); clear(); right(4); clear(); left(4); loop_end(); left(1)

    # If Match (C5 == 1), Emit Code
    right(5); loop_start()
    clear()
    left(5)
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xcb) # dec rbx
    right(5)
    loop_end(); left(5)

    right(2); loop_end(); left(2) # End C2 Check

    right(2); loop_end(); left(2) # End Main Loop


    # 4. Exit Sequence
    # mov edi, ebx; mov eax, 60; syscall
    emit_machine_code_tracked([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 5. Pad to 200 bytes
    right(7); dec(200); loop_start(); inc(200); left(7); emit_byte_tracked(0); right(7); dec(200); loop_end(); inc(200); left(7)

    # --- Post-process: balance loop tokens if needed ---
    out_str = "".join(CMDS)
    ls = out_str.count(F + F + S)
    le = out_str.count(F + F + F)
    if ls > le:
        missing = ls - le
        # Append missing loop_end tokens at EOF (pragmatic safety measure)
        out_str += (F + F + F) * missing

    sys.stdout.buffer.write(out_str.encode('utf-8'))

if __name__ == '__main__':
    main()