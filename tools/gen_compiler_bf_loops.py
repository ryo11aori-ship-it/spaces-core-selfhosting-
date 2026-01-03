#!/usr/bin/env python3
import sys

# --- Basic Config ---
TARGET_SIZE = 12000 # 12KB to prevent Segfault
LOAD_ADDR = 0x400000

# --- Helper Functions (One-liners) ---
def emit(s): sys.stdout.write(s + "\n")
def right(n): emit((" " * 3) * n)
def left(n): emit((" " * 2 + "\u3000") * n)
def inc(n): emit((" " + "\u3000" + " ") * n)
def dec(n): emit((" " + "\u3000" + "\u3000") * n)
def out(): emit("\u3000" + " " + " ")
def inp(): emit("\u3000" + " " + "\u3000")
def l_open(): emit("\u3000" + "\u3000" + " ")
def l_close(): emit("\u3000" + "\u3000" + "\u3000")
def clear(): l_open(); dec(1); l_close()

# --- Memory Layout ---
# 100: Input Character
# 101: Temp Copy (for checking)
# 102: Match Flag
# 200: Output Helper

def main():
    # 1. Prepare Headers (Static)
    h = [0x7f,0x45,0x4c,0x46,0x02,0x01,0x01,0x00,0,0,0,0,0,0,0,0,0x02,0x00,0x3e,0x00,0x01,0x00,0x00,0x00]
    # Entry point address
    h += list((LOAD_ADDR + 120).to_bytes(8, "little"))
    h += list((64).to_bytes(8, "little"))
    h += list((0).to_bytes(8, "little"))
    h += list((0).to_bytes(4, "little"))
    h += [0x40,0x00,0x38,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00] # Phdr start

    # Program Header
    ph = [0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00]
    ph += list((0).to_bytes(8, "little"))
    ph += list((LOAD_ADDR).to_bytes(8, "little"))
    ph += list((LOAD_ADDR).to_bytes(8, "little"))
    ph += list((TARGET_SIZE).to_bytes(8, "little"))
    ph += list((0x10000).to_bytes(8, "little"))
    ph += list((0x1000).to_bytes(8, "little"))

    # Initial Code Stub (Setup registers)
    stub = [0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00]

    full_header = h + ph + stub
    current_size = len(full_header)

    # 2. Emit Header (Using Output Cell 200)
    # Start at 0, move to 200
    right(200)
    for b in full_header:
        clear()
        if b > 0: inc(b)
        out()
    # Return to 100 (Input Cell)
    left(100)

    # 3. Read First Char
    inp()

    # 4. Main Loop (While Input != 0)
    l_open()

    # --- BLOCK: Check '+' (43) ---
    # Copy 100 -> 101
    l_open(); dec(1); right(1); inc(1); left(1); l_close() # Move to 101
    right(1); l_open(); dec(1); left(1); inc(1); right(1); l_close(); left(1) # Restore 100
    # Check 101
    right(1); dec(43) # Subtract 43
    # If 0, Set Flag 102
    right(1); clear(); inc(1); left(1) # Flag=1 initially
    l_open(); right(1); dec(1); left(1); l_open(); dec(1); l_close(); l_close() # If 101!=0, Flag=0
    # Check Flag 102
    right(1); l_open()
    # Emit Code for '+'
    dec(1); right(98) # Move to 200
    clear(); inc(0xfe); out()
    clear(); inc(0x03); out()
    left(98) # Back to 102
    l_close()
    left(2) # Back to 100
    current_size += 2

    # --- BLOCK: Check ',' (44) ---
    l_open(); dec(1); right(1); inc(1); left(1); l_close()
    right(1); l_open(); dec(1); left(1); inc(1); right(1); l_close(); left(1)
    right(1); dec(44)
    right(1); clear(); inc(1); left(1)
    l_open(); right(1); dec(1); left(1); l_open(); dec(1); l_close(); l_close()
    right(1); l_open()
    dec(1); right(98)
    # Emit Code for ',' (Syscall Read)
    clear(); inc(0xb8); out(); clear(); out(); clear(); out(); clear(); out(); clear(); out()
    clear(); inc(0xbf); out(); clear(); out(); clear(); out(); clear(); out(); clear(); out()
    clear(); inc(0x48); out(); clear(); inc(0x89); out(); clear(); inc(0xde); out()
    clear(); inc(0xba); out(); clear(); inc(0x01); out(); clear(); out(); clear(); out(); clear(); out()
    clear(); inc(0x0f); out(); clear(); inc(0x05); out()
    left(98); l_close()
    left(2)
    current_size += 20

    # --- BLOCK: Check '-' (45) ---
    l_open(); dec(1); right(1); inc(1); left(1); l_close()
    right(1); l_open(); dec(1); left(1); inc(1); right(1); l_close(); left(1)
    right(1); dec(45)
    right(1); clear(); inc(1); left(1)
    l_open(); right(1); dec(1); left(1); l_open(); dec(1); l_close(); l_close()
    right(1); l_open()
    dec(1); right(98)
    clear(); inc(0xfe); out()
    clear(); inc(0x0b); out()
    left(98); l_close()
    left(2)
    current_size += 2

    # --- BLOCK: Check '.' (46) ---
    l_open(); dec(1); right(1); inc(1); left(1); l_close()
    right(1); l_open(); dec(1); left(1); inc(1); right(1); l_close(); left(1)
    right(1); dec(46)
    right(1); clear(); inc(1); left(1)
    l_open(); right(1); dec(1); left(1); l_open(); dec(1); l_close(); l_close()
    right(1); l_open()
    dec(1); right(98)
    # Emit Code for '.' (Syscall Write)
    clear(); inc(0xb8); out(); clear(); inc(1); out(); clear(); out(); clear(); out(); clear(); out()
    clear(); inc(0xbf); out(); clear(); inc(1); out(); clear(); out(); clear(); out(); clear(); out()
    clear(); inc(0x48); out(); clear(); inc(0x89); out(); clear(); inc(0xde); out()
    clear(); inc(0xba); out(); clear(); inc(0x01); out(); clear(); out(); clear(); out(); clear(); out()
    clear(); inc(0x0f); out(); clear(); inc(0x05); out()
    left(98); l_close()
    left(2)
    current_size += 20

    # --- BLOCK: Check '<' (60) ---
    l_open(); dec(1); right(1); inc(1); left(1); l_close()
    right(1); l_open(); dec(1); left(1); inc(1); right(1); l_close(); left(1)
    right(1); dec(60)
    right(1); clear(); inc(1); left(1)
    l_open(); right(1); dec(1); left(1); l_open(); dec(1); l_close(); l_close()
    right(1); l_open()
    dec(1); right(98)
    clear(); inc(0x48); out()
    clear(); inc(0xff); out()
    clear(); inc(0xcb); out()
    left(98); l_close()
    left(2)
    current_size += 3

    # --- BLOCK: Check '>' (62) ---
    l_open(); dec(1); right(1); inc(1); left(1); l_close()
    right(1); l_open(); dec(1); left(1); inc(1); right(1); l_close(); left(1)
    right(1); dec(62)
    right(1); clear(); inc(1); left(1)
    l_open(); right(1); dec(1); left(1); l_open(); dec(1); l_close(); l_close()
    right(1); l_open()
    dec(1); right(98)
    clear(); inc(0x48); out()
    clear(); inc(0xff); out()
    clear(); inc(0xc3); out()
    left(98); l_close()
    left(2)
    current_size += 3

    # --- Next Char ---
    inp()
    l_close()

    # 5. Finalize (Exit Code + Padding)
    right(100) # Move to 200
    # Emit Exit Syscall
    clear(); inc(0x48); out()
    clear(); inc(0x31); out()
    clear(); inc(0xff); out()
    clear(); inc(0xb8); out(); clear(); inc(0x3c); out(); clear(); out(); clear(); out(); clear(); out()
    clear(); inc(0x0f); out(); clear(); inc(0x05); out()
    current_size += 10

    # Emit Zero Padding (Simple loop)
    # We need to fill up to TARGET_SIZE.
    pad_len = TARGET_SIZE - current_size
    # Use 201 as counter
    right(1); clear(); inc(pad_len // 100); # 100 bytes per loop
    l_open()
    dec(1); left(1)
    # Emit 100 zeros
    for _ in range(100):
        clear(); out()
    right(1)
    l_close()

if __name__ == "__main__":
    main()
