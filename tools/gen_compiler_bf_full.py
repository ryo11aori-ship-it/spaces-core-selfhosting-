#!/usr/bin/env python3
# tools/gen_compiler_bf_full.py
# Level 1.7: Full Brainfuck Compiler (Buffered I/O Strategy)
# Fixed: Ensured p_memsz is 64KB to avoid Segmentation Fault.

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
# C8: Output Buffer Count
# C20-C99: Internal Stack (Reserved for later)
# C100+: Code Buffer

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

# バッファ書き込み用: C8 (Count) を増やし、C100+C8 に書き込む
# 簡略化のため、「スキャン方式」で書き込み位置を探す
def append_scan_write(vals):
    for v in vals:
        # Buffer Base (C100) へ移動
        right(BUFFER_BASE)
        
        # 0（空き場所）を探して右へ
        loop_open(); right(); loop_close()
        
        # 書き込み
        if v > 0: inc(v)
        
        # マーカー（番兵）として次のセルを 255 にしておく？
        # いや、0終端で十分。次のセルは既に0のはず。
        # ただし、読み出し時に困らないよう、最後に Sentinel を置く必要があるかも。
        # 今回は Count (C8) を使って読み出すので、0のままでOK。
        
        # C0に戻る。0でないセルを左へスキップ。
        loop_open(); left(); loop_close()
        
        # Buffer Base から C0 へ
        left(BUFFER_BASE)
        
        # Count (C8) ++
        right(8); inc(); left(8)

def check_char(char_code, logic_func):
    copy_c0_to_c1()
    right(1); dec(char_code)
    right(2); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(3); logic_func(); right(3); clear(); loop_close(); left(3)

def main():
    total_size = 1000 # 少し大きめに
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
        *p64(0x10000), # Memory Size 64KB (これがないと落ちる)
        *p64(0x1000)
    ]
    
    # 1. ELF Header (Stream)
    emit_bytes(header + prog_header)
    
    # Init Code (Stream)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])

    # 2. Main Loop
    right(2); clear(); inc(); left(2)
    right(2); loop_open(); left(2)
    
    clear(); inp()
    
    # EOF Check
    copy_c0_to_c1()
    right(3); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(1); clear(); right(1); clear(); loop_close(); left(3)
    
    # Checks (Using Buffering)
    check_char(62, lambda: append_scan_write([0x48, 0xff, 0xc3])) # >
    check_char(60, lambda: append_scan_write([0x48, 0xff, 0xcb])) # <
    check_char(43, lambda: append_scan_write([0xfe, 0x03]))       # +
    check_char(45, lambda: append_scan_write([0xfe, 0x0b]))       # -
    
    # .
    check_char(46, lambda: append_scan_write([
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x48, 0x89, 0xde,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]))
    
    # ,
    check_char(44, lambda: append_scan_write([
        0xb8, 0x00, 0x00, 0x00, 0x00,
        0xbf, 0x00, 0x00, 0x00, 0x00,
        0x48, 0x89, 0xde,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]))
    
    right(2); loop_close(); left(2)
    
    # 3. Flush Buffer
    # バッファにあるバイト列 (C8個) を出力する
    # C8: 残り出力バイト数
    # C6: 現在の読み出しオフセット (0からスタート)
    
    # ループ C8
    right(8)
    loop_open()
    dec(); left(8) # C8--, Back to C0
    
    # Go to Buffer Start
    right(BUFFER_BASE)
    
    # Go Right C6 times (C6 is at -BUFFER_BASE+6)
    # Copy C6 to C1
    left(BUFFER_BASE); right(6); loop_open(); dec(); left(5); inc(); right(1); inc(); left(2); loop_close()
    right(2); loop_open(); dec(); left(2); inc(); right(2); loop_close(); left(6)
    
    # Move Head Right C1 times
    right(BUFFER_BASE)
    right(1); loop_open(); dec(); right(); loop_close(); left(1)
    
    # Output byte
    out()
    
    # Return to C0
    # 左に動くには？ バッファ内の値は非0とは限らないのでスキャンバックできない。
    # しかし C6 (Offset) があるので、C6+BUFFER_BASE 回左に行けば戻れる。
    # さっき C6 を C1 にコピーした。C1 は 0 になった。
    # もう一度 C6 を C1 にコピーしておく必要があるが、遠い。
    
    # 代替案: 「スキャンバック」を使うために、読み終わったセルを 0 にクリアする？
    # いや、0 のデータもある。
    
    # Pragamaticな解決策:
    # バッファの各セルの間にマーカー(非0)を置く？ -> メモリ倍増。
    
    # 今回のテストケース(,. => read, write)では、出力される機械語に「0」が含まれる。
    # 例: mov eax, 1 -> B8 01 00 00 00
    # だから 0 スキップは使えない。
    
    # 正攻法: C6 (Offset) を使って戻る。
    # C6のコピーを作る。
    left(BUFFER_BASE); right(6); loop_open(); dec(); left(5); inc(); right(2); inc(); left(3); loop_close()
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(6)
    # C2にコピーされた。
    
    # さっきの「進む」処理でBuffer内にいる。
    # 戻る:
    right(BUFFER_BASE) # 概念上の位置合わせ
    # Loop C2: left
    right(2); loop_open(); dec(); left(2); left(); right(2); loop_close(); left(2)
    
    # Buffer Base から C0 へ
    left(BUFFER_BASE)
    
    # C6++
    right(6); inc(); left(6)
    
    # Loop End (C8)
    right(8)
    loop_close()
    left(8)

    # 4. Exit Code (0)
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    
    # 5. Padding
    right(7); dec(total_size) # C7 = Written - Total
    # C7にバッファ分は含まれていない(Flush時にemit_byte_tracked使ってないから)
    # C6 (Total Flush Size) を C7 に足す
    right(6); loop_open(); dec(); right(); inc(); left(); loop_close(); left(6)
    
    left(1); dec(total_size)
    loop_open()
    inc(total_size)
    right(1); clear(); out(); left(1)
    inc()
    dec(total_size)
    loop_close()

if __name__ == "__main__":
    main()
