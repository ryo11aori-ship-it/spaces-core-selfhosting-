#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Brainfuckを経由せず、Spacesコードを直接生成します。
# インデントエラーを防ぐため、関数をネストさせずに記述しています。

import sys

# --- Global Constants & Buffer ---
S = " "      # Space
F = "\u3000" # Fullwidth Space
CMDS = []

# --- Basic Spaces Instructions ---
def emit(s):
    CMDS.append(s)

def right(n=1):
    for _ in range(n): emit(S+S+S)

def left(n=1):
    for _ in range(n): emit(S+S+F)

def inc(n=1):
    for _ in range(n): emit(S+F+S)

def dec(n=1):
    for _ in range(n): emit(S+F+F)

def out():
    emit(F+S+S)

def inp():
    emit(F+S+F)

def loop_start():
    emit(F+F+S)

def loop_end():
    emit(F+F+F)

# --- High Level Helpers ---
def clear():
    loop_start()
    dec()
    loop_end()

def emit_byte(val):
    # 値を設定して出力し、クリアして戻る
    right()
    clear()
    inc(val)
    out()
    clear()
    left()

def emit_machine_code(bytes_list):
    # 機械語列を出力する (C7を作業領域として使用)
    for b in bytes_list:
        right(2)
        clear()
        inc(b)
        out()
        clear()
        left(2)

def read_valid_bit(weight):
    # C0: Input
    # ループ開始 (C0 != 0)
    clear()
    inc()
    loop_start() 
    
    inp() # Read C0
    
    loop_start() # Check EOF (0)
    
    # Check 255 (EOF)
    right()
    clear()
    inc()
    left() # C1 = 1
    
    inc() # C0 += 1
    loop_start() # If C0!=0
    dec() # Restore C0
    right()
    dec() # C1 = 0
    left()
    loop_end()
    
    # If C1 is 1 (EOF found), Exit All
    right()
    loop_start()
    # Clear C6, C1, C0
    right(5); clear(); left(5)
    clear()
    left(); clear()
    loop_end()
    left() # Back to C0
    
    # Clear Flags C2, C3, C4
    right(2); clear()
    right(); clear()
    right(); clear()
    left(4)
    
    # Copy C0 -> C1 using C4
    right(); clear(); right(); clear(); right(); clear(); left(3)
    loop_start(); right(); inc(); right(3); inc(); left(4); dec(); loop_end()
    right(4); loop_start(); left(4); inc(); right(4); dec(); loop_end()
    left(4)
    
    # Check S (32) on C1
    right(); clear(); inc(); left() # C2=1 (Assume S)
    right(); dec(32)
    loop_start() # If C1!=0 (Not S)
    clear(); right(); clear(); left() # Clear C1, C2
    
    # Check F (227)
    left() # To C0
    loop_start(); right(); inc(); right(3); inc(); left(4); dec(); loop_end() # Copy
    right(4); loop_start(); left(4); inc(); right(4); dec(); loop_end() # Restore
    left() # To C3 (Layout: C0 C1 C2 C3)
    right(3); clear(); inc(); left(3) # C3=1 (Assume F)
    right(); dec(227) # C1 -= 227
    loop_start() # If C1!=0 (Not F)
    clear(); right(2); clear(); left(2) # Clear C1, C3
    loop_end()
    loop_end() # End Not S
    
    # Check Flags C2, C3. If set, Clear C0 to Exit Loop
    right(2) # To C2
    loop_start(); left(2); clear(); right(2); dec(); inc(); loop_end()
    right() # To C3
    loop_start(); left(3); clear(); right(3); dec(); inc(); loop_end()
    left(3) # Back to C0
    
    loop_end() # End Not 255
    loop_end() # End Not 0
    loop_end() # End Search Loop
    
    # Action Phase
    # If F (C3=1), Add Weight to C6
    right(3)
    loop_start()
    clear()
    left(3); inp(); inp() # Consume 2 chars
    right(6); inc(weight); left(6) # Add to C6
    right(3)
    loop_end()
    
    # If S (C2=1), Clear C2
    left(); clear()
    left(2) # Back to C0

def main():
    # 1. Safety Margin
    right(8)

    # 2. ELF Header (Allow 131KB memory to prevent SegFault)
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # p_filesz 131KB
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # p_memsz 131KB
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header:
        emit_byte(b)

    # 3. Init Code
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code:
        emit_byte(b)

    # 4. Main Compiler Loop
    right(6); clear(); inc(); loop_start() # C6=1, Loop
    
    left(); clear() # Clear C5 (Acc)
    left(5) # To C0
    
    read_valid_bit(4)
    right(6); loop_start(); left(6)
    read_valid_bit(2)
    right(6); loop_start(); left(6)
    read_valid_bit(1)
    right(6); loop_start(); left(6)
    
    left() # To C5 (Acc)
    
    # Case 0: >
    right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x49, 0xff, 0xc5])
    clear(); loop_end(); left()
    
    # Case 1: <
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x49, 0xff, 0xcd])
    clear(); loop_end(); left()

    # Case 2: +
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x41, 0xfe, 0x45, 0x00])
    clear(); loop_end(); left()

    # Case 3: -
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x41, 0xfe, 0x4d, 0x00])
    clear(); loop_end(); left()

    # Case 4: .
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05
    ])
    clear(); loop_end(); left()

    # Case 5: ,
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); clear(); loop_end(); left()

    # Case 6: [
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    clear(); loop_end(); left()
    
    # Case 7: ]
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    clear(); loop_end(); left()
    
    right() # To C6
    loop_end(); loop_end(); loop_end() # Close checks
    loop_end() # End Main Loop
    
    # Padding
    right(2); clear(); inc(255); loop_start()
    right(); clear(); inc(255); loop_start()
    right(); out(); left(); dec()
    loop_end(); left(); dec()
    loop_end()
    
    # Output
    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))

if __name__ == '__main__':
    main()
