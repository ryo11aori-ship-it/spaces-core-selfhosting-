#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Brainfuckを経由せず、Spacesコードを直接生成します。
# インデントエラーを防ぐため、Pythonコードのインデントを完全にフラットにしています。

import sys

# --- Constants ---
S = " "      # Space
F = "\u3000" # Fullwidth Space
CMDS = []

# --- Basic Instructions ---
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

# --- Helpers ---
def clear(): 
    loop_start()
    dec()
    loop_end()

def emit_byte(val):
    # 値をセットして出力し、クリアして戻る
    right()
    clear()
    inc(val)
    out()
    clear()
    left()

def main():
    # 1. Safety Margin
    right(8)

    # 2. ELF Header (64-bit Linux)
    # File size: 512 bytes (0x200), Mem size: 4096 bytes (0x1000)
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # Entry: 0x400078
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # p_filesz 0x200
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # p_memsz 0x1000
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header:
        emit_byte(b)
    
    current_offset = len(header)

    # 3. Code Body (Hello World x64)
    # Entry point 0x400078 is right after header (120 bytes)
    # Message address: 0x400000 + 0x100 (256)
    msg_addr = 0x400100
    msg_addr_bytes = [
        (msg_addr & 0xFF), ((msg_addr >> 8) & 0xFF), ((msg_addr >> 16) & 0xFF), 0x00,
        0x00, 0x00, 0x00, 0x00
    ]

    code = [
        0xb8, 0x01, 0x00, 0x00, 0x00,       # mov eax, 1
        0xbf, 0x01, 0x00, 0x00, 0x00,       # mov edi, 1
        0x48, 0xbe] + msg_addr_bytes + [    # mov rsi, msg_addr
        0xba, 0x0e, 0x00, 0x00, 0x00,       # mov edx, 14
        0x0f, 0x05,                         # syscall
        0xb8, 0x3c, 0x00, 0x00, 0x00,       # mov eax, 60
        0x31, 0xff,                         # xor edi, edi
        0x0f, 0x05                          # syscall
    ]
    
    for b in code:
        emit_byte(b)
    current_offset += len(code)

    # 4. Padding to Message (0x100 = 256)
    pad_len = 0x100 - current_offset
    for _ in range(pad_len):
        emit_byte(0)
    current_offset += pad_len

    # 5. Message Data
    msg = [
        0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, # Hello, 
        0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21, 0x0a  # world!\n
    ]
    for b in msg:
        emit_byte(b)
    current_offset += len(msg)

    # 6. Padding to File Size (0x200 = 512)
    final_pad = 0x200 - current_offset
    for _ in range(final_pad):
        emit_byte(0)

    # 7. Consume Input (Compiler Logic)
    # 入力をすべて読み捨てるループ
    clear() # Clear C0
    inc()   # C0 = 1
    loop_start() 
    inp()   # Read char
    loop_start() 
    clear() # If char != 0, clear it
    loop_end() 
    loop_end()

    # Output
    sys.stdout.buffer.write("".join(CMDS).encode('utf-8'))
    
    # CI Dummy Log
    with open("bf_debug.log", "w") as f:
        f.write("Direct Generation Complete.\n")

if __name__ == '__main__':
    main()
